from models.db_schemes import Product
from models.BaseDataModel import BaseDataModel
from models import DataBaseEnum
from sqlalchemy import select, delete, func

class ProductModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client = db_client


    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        return instance

    async def create_product(self, data:dict):
        async with self.db_client() as session:
            async with session.begin():
                product = Product(**data)
                session.add(product)
                await session.flush() ## flush() => flushes the session to the database
                product_id = product.product_id
        return product_id    

    # async def get_all_products(self, page:int=1, page_size:int=10):
    # ## pagination: it is a technique to divide the data into pages and retrieve them one by one
    #     async with self.db_client() as session:
    #         async with session.begin():
    #             query = select(Product).offset((page -1)*page_size).limit(page_size)
    #             products = session.execute(query).scalars().all()
    #             return products
    async def get_products_batch(
        self,
        last_id: int = 0,
        batch_size: int = 50
    ):
        async with self.db_client() as session:
            query = (
                select(Product)
                .where(Product.product_id > last_id)
                .order_by(Product.product_id)
                .limit(batch_size)
            )

            result = await session.execute(query)

            return result.scalars().all()

    # async def get_product_by_id(self,product_id):
    #     async with self.db_client() as session:
    #         async with session.begin():
    #             query = select(Product).where(product_id=product_id)
    #             product = session.execute(query).scalar_one_or_none()
    #             if product is None:
    #                 record = Product(product_id=product_id)
    #                 product = await self.create_product(record)
    #                 return product
    #             else:
    #                 return product
    async def get_product_by_id(self, product_id: int):

        async with self.db_client() as session:
            return await session.get(Product, product_id)