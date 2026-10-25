import json
from controllers import BaseController
from models.db_schemes.minirag.schemes import Product
from models import ProductModule
from models.db_schemes.minirag.schemes import RetrievedProduct
from stores.vectoredb.providers.PGVectorDB import PGVectorDB
import asyncio
from typing import List
class CatalogController(BaseController):

    def __init__(self, vectordb_client, embedding_client, generation_client, product_model:ProductModule):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.product_model = product_model

    def build_searchable_text(self, product:Product):
        def normalize(value):
            if value is None:
                return ""
            if isinstance(value, (list, tuple, set)):
                return ", ".join(str(v) for v in value)
            return str(value)

        fields = {
            "Product": product.name,
            "Category": product.category,
            "Color": product.color,
            "Material": product.material,
            "Occasions": product.occasions,
            "Style": product.style,
            "Description": product.description,
        }

        # Include optional attributes if available
        for attr in ("brand", "fit"):
            value = getattr(product, attr, None)
            if value:
                fields[attr.capitalize()] = value

        return "\n".join(
            f"{field}: {normalize(value)}"
            for field, value in fields.items()
            if value is not None and normalize(value)
        )

    async def index_products(self, products:List[Product])-> int:

        if not products:
            return 0
        
        product_ids = [
            product.product_id
            for product in products
        ]

        texts = [self.build_searchable_text(product=product)
                for product in products]
        
        vectors = await asyncio.to_thread(
            self.embedding_client.embed_text,
            text=texts
        )
        return await self.vectordb_client.upsert_product_search_index(product_ids=product_ids,texts=texts,vectors=vectors)


    ## index single product
    async def index_one_product(self, product_id):
        product = await self.product_model.get_product_by_id(product_id=product_id)

        if not product:
            return None
        
        if product is None:
            raise ValueError(
                f"Product {product_id} does not exist"
            )
        
        return await self.index_products([product])


    
    #index existing products
    # async def index_all_products(self, products, batch_size:int = 50) -> int:
    #     """"index alll existings products in the database"""
        
    #     if not products:
    #         raise ValueError("No products found in the database")

    #     total_products = len(products)
    #     total_indexed = 0
    #     for i in range(0,total_products, batch_size):
    #         batch_end = i + batch_size
    #         batch = products[i:batch_end]
    #         total_indexed += await self.index_products(batch)
    #     return total_indexed
    async def index_all_products(
        self,
        batch_size: int = 50
    ) -> int:

        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        total_indexed = 0
        last_id = 0

        while True:
            products = await self.product_model.get_products_batch(
                last_id=last_id,
                batch_size=batch_size
            )

            if not products:
                break

            print(f"Fetched products: {len(products)}")
            print(f"Last ID: {last_id}")

            if not products:
                print("No more products found!")
                break

            print(f"Product IDs: {[p.product_id for p in products]}")

            indexed_count = await self.index_products(products)

            print(f"Indexed count returned: {indexed_count}")

            total_indexed += indexed_count
            last_id = products[-1].product_id

        return total_indexed


    def reciprocal_rank_fusion(
        self,
        semantic_results: List[RetrievedProduct],
        keyword_results: List[RetrievedProduct],
        limit: int = 5,
        k: int = 60
    ) -> List[RetrievedProduct]:

        rrf_scores = {}
        doc_map = {}

        for results in [semantic_results, keyword_results]:
            for rank, doc in enumerate(results, start=1):

                product_id = doc.product_id

                if product_id is None:
                    raise ValueError("RRF requires a product_id")

                rrf_scores[product_id] = (
                    rrf_scores.get(product_id, 0)
                    + 1 / (k + rank)
                )

                doc_map[product_id] = doc

        sorted_ids = sorted(
            rrf_scores,
            key=rrf_scores.get,
            reverse=True
        )

        return [
            RetrievedProduct(
                text=doc_map[product_id].text,
                product_id=product_id,
                score=rrf_scores[product_id]
            )
            for product_id in sorted_ids[:limit]
        ]

    async def hybrid_search(self, query, limit:int=5, **filters):
        candidate_limit = limit * 4
        # print(f"query: {query}")
        vector = await asyncio.to_thread(self.embedding_client.embed_text, text=query)
        seamntic_results, keyword_results = await asyncio.gather(
            self.vectordb_client.search_product_by_vector(vector=vector[0], limit=candidate_limit, **filters),
            self.vectordb_client.search_product_keyword(query=query, limit=candidate_limit, **filters)
        )
        # print(f"seamntic_results: {seamntic_results}")
        # print(f"keyword_results: {keyword_results}")
        return self.reciprocal_rank_fusion(seamntic_results, keyword_results, limit=limit)