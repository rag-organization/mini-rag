import asyncio
from decimal import Decimal
from itertools import product as combinations
from sqlalchemy import select

# Adapt these imports to your project
from models.db_schemes.minirag.schemes import Product, ProductVariant


class OutfitService:

    def __init__(self, db_client, catalog_controller):
        self.db_client = db_client
        self.catalog_controller = catalog_controller

    async def build_outfit(
        self,
        occasion: str,
        categories: list[str],
        max_budget: float | None = None,
        sizes: dict[str, str] | None = None
    ) -> dict:

        if not 1 <= len(categories) <= 4:
            raise ValueError("Choose between 1 and 4 categories")

        if len(set(c.lower() for c in categories)) != len(categories):
            raise ValueError("Categories must be unique")

        budget = (
            Decimal(str(max_budget))
            if max_budget is not None
            else None
        )

        # 1. Search relevant products for each category
        search_results = await asyncio.gather(
            *[
                self.catalog_controller.hybrid_search(
                    query=f"{occasion} {category}",
                    limit=40
                )
                for category in categories
            ]
        )

        # 2. Collect retrieved product IDs
        product_ids = list(dict.fromkeys(
            hit.product_id
            for results in search_results
            for hit in (results or [])
        ))

        if not product_ids:
            return {
                "status": "no_products",
                "message": "No matching products found"
            }

        # 3. Fetch real product and stock information
        async with self.db_client() as session:

            products_result = await session.execute(
                select(Product).where(
                    Product.product_id.in_(product_ids)
                )
            )

            variants_result = await session.execute(
                select(ProductVariant).where(
                    ProductVariant.product_id.in_(product_ids)
                )
            )

            products = products_result.scalars().all()
            variants = variants_result.scalars().all()

        product_map = {
            p.product_id: p for p in products
        }

        variants_map = {}

        for variant in variants:
            variants_map.setdefault(
                variant.product_id, []
            ).append(variant)

        # 4. Build candidates for every outfit category
        candidate_groups = []

        for category, hits in zip(categories, search_results):

            candidates = []
            requested_size = (sizes or {}).get(category)

            for rank, hit in enumerate(hits or [], start=1):

                item = product_map.get(hit.product_id)

                if item is None:
                    continue

                if item.category.lower() != category.lower():
                    continue

                if getattr(item, "is_active", True) is False:
                    continue

                price = Decimal(str(item.price))

                if budget is not None and price > budget:
                    continue

                available_variants = [
                    v for v in variants_map.get(item.product_id, [])
                    if v.stock > 0
                    and (
                        requested_size is None
                        or v.size.lower() == requested_size.lower()
                    )
                ]

                if not available_variants:
                    continue

                candidates.append({
                    "product_id": item.product_id,
                    "name": item.name,
                    "category": item.category,
                    "color": item.color,
                    "price": price,
                    "currency": getattr(item, "currency", "MAD"),
                    "image_url": item.image_url,
                    "available_sizes": [
                        v.size for v in available_variants
                    ],
                    "rank_score": 1 / (60 + rank)
                })

                if len(candidates) == 5:
                    break

            if not candidates:
                return {
                    "status": "missing_category",
                    "category": category,
                    "message": (
                        f"No available products found for {category}"
                    )
                }

            candidate_groups.append(candidates)

        # 5. Find the highest-ranked combination within budget
        best_outfit = None
        best_score = float("-inf")
        best_price = None

        for outfit in combinations(*candidate_groups):

            # Avoid using one product for multiple slots
            ids = [item["product_id"] for item in outfit]

            if len(set(ids)) != len(ids):
                continue

            # Do not combine different currencies
            if len(set(item["currency"] for item in outfit)) != 1:
                continue

            total = sum(
                (item["price"] for item in outfit),
                Decimal("0")
            )

            if budget is not None and total > budget:
                continue

            score = sum(
                item["rank_score"] for item in outfit
            )

            if (
                score > best_score
                or (
                    score == best_score
                    and (best_price is None or total < best_price)
                )
            ):
                best_outfit = outfit
                best_score = score
                best_price = total

        if best_outfit is None:
            return {
                "status": "budget_exceeded",
                "message": (
                    "No complete outfit satisfies the budget "
                    "and availability constraints"
                )
            }

        # 6. Return structured catalog products
        return {
            "status": "success",
            "occasion": occasion,
            "products": [
                {
                    key: str(value) if key == "price" else value
                    for key, value in item.items()
                    if key != "rank_score"
                }
                for item in best_outfit
            ],
            "total_price": str(best_price),
            "currency": best_outfit[0]["currency"],
            "note": (
                "Suggested products are available, but "
                "individual sizes and styling preferences "
                "should be confirmed."
            )
        }