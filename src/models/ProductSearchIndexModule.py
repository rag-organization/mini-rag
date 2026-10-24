# from models.db_schemes import ProductSearchIndex
# from models.BaseDataModel import BaseDataModel
# from models import DataBaseEnum
# from sqlalchemy import select, delete, func

# class ProductSearchIndexModel(BaseDataModel):
#     def __init__(self, db_client):
#         super().__init__(db_client)
#         self.db_client = db_client


#     @classmethod
#     async def create_instance(cls, db_client:object):
#         instance = cls(db_client)
#         return instance

#     async def create_project(self, product_search_index:ProductSearchIndex):
#         async with self.db_client() as session:
#             async with session.begin():
#                 session.add(product_search_index)
#             await session.refresh(product_search_index)
#         return product_search_index    


    