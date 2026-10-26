from decimal import Decimal

from sqlalchemy import select, func


# Adapt to your actual model paths
from models.db_schemes.minirag.schemes import Product, SizeChart, ProductVariant



class CatalogToolsService:

    def __init__(self, db_client):
        self.db_client = db_client

    async def check_stock(
        self,
        product_id: int,
        size: str | None = None
    ) -> dict:

        async with self.db_client() as session:

            product = await session.get(Product, product_id)

            if product is None:
                return {
                    "found": False,
                    "message": "Product not found"
                }

            query = select(ProductVariant).where(
                ProductVariant.product_id == product_id
            )

            if size:
                query = query.where(
                    func.lower(ProductVariant.size) == size.lower()
                )

            result = await session.execute(query)
            variants = result.scalars().all()

        available_variants = [
            {
                "size": variant.size,
                "stock": variant.stock,
                "available": variant.stock > 0
            }
            for variant in variants
        ]

        return {
            "found": True,
            "product_id": product_id,
            "product_name": product.name,
            "requested_size": size,
            "available": any(
                v["available"] for v in available_variants
            ),
            "variants": available_variants
        }

    async def recommend_size(
        self,
        product_id: int,
        chest_cm: float | None = None,
        waist_cm: float | None = None,
        hip_cm: float | None = None
      ) -> dict:
  
          async with self.db_client() as session:
  
              product = await session.get(Product, product_id)
  
              if product is None:
                  return {
                      "found": False,
                      "message": "Product not found"
                  }
  
              charts_result = await session.execute(
                  select(SizeChart).where(
                      SizeChart.product_id == product_id
                  )
              )
  
              charts = charts_result.scalars().all()
  
              variants_result = await session.execute(
                  select(ProductVariant).where(
                      ProductVariant.product_id == product_id
                  )
              )
  
              variants = variants_result.scalars().all()
  
          if not charts:
              return {
                  "found": True,
                  "message": "No size chart available for this product",
                  "recommended_sizes": []
              }
  
          stock_by_size = {
              v.size.upper(): v.stock
              for v in variants
          }
  
          measurements = {
              "chest": chest_cm,
              "waist": waist_cm,
              "hip": hip_cm
          }
  
          supplied = {
              name: Decimal(str(value))
              for name, value in measurements.items()
              if value is not None
          }
  
          if not supplied:
              return {
                  "found": True,
                  "message": "Customer measurements are required",
                  "available_sizes": [
                      {
                          "size": chart.size_label,
                          "stock": stock_by_size.get(
                              chart.size_label.upper(), 0
                          )
                      }
                      for chart in charts
                  ],
                  "recommended_sizes": []
              }
  
          recommendations = []
  
          for chart in charts:
  
              matches = True
  
              for measurement, value in supplied.items():
  
                  minimum = getattr(
                      chart, f"{measurement}_min_cm"
                  )
                  maximum = getattr(
                      chart, f"{measurement}_max_cm"
                  )
  
                  if (
                      minimum is None
                      or maximum is None
                      or not minimum <= value <= maximum
                  ):
                      matches = False
                      break
  
              if matches:
                  stock = stock_by_size.get(
                      chart.size_label.upper(), 0
                  )
  
                  recommendations.append({
                      "size": chart.size_label,
                      "available": stock > 0,
                      "stock": stock
                  })
  
          return {
              "found": True,
              "product_id": product_id,
              "product_name": product.name,
              "recommended_sizes": recommendations,
              "measurement_unit": "cm",
              "note": (
                  "Recommendations use the retailer's size chart. "
                  "Actual fit may vary by garment and fit preference."
              )
          }