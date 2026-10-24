from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
import os
from controllers.CatalogController import CatalogController
from models.ProductModule import ProductModel
from models.db_schemes.minirag.schemes import Product
from models.enums.ResponseEnum import ResponseSignal
import logging

from routes.schemas.product import ProductCreate,SearchProduct
product_router = APIRouter(
    prefix="/api/v1/product",
    tags=["api_v1", "product"],
)


@product_router.get("/")
async def root():
    return {"message": "product api"}


## uplad product
@product_router.post("/upload_product")
async def upload_product(request: Request, playload:ProductCreate):

    product_model = await ProductModel.create_instance(request.app.vector_db_client.db_client)
    product_id = await product_model.create_product(data=playload.model_dump())
    catalog_controller = CatalogController(
        vectordb_client = request.app.vector_db_client, 
        embedding_client = request.app.embedding_client, 
        generation_client = request.app.generation_client,
        product_model = product_model
    )
    try:
        indexed_count = await catalog_controller.index_one_product(
            product_id=product_id
        )
    except Exception:
        logging.getLogger("uvicorn").exception(
            "Indexing failed for product %s", product_id
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Product created, but indexing failed. Reindex required.",
                "product_id": product_id,
                "indexed": False
            }
        )


    return {
        "message": ResponseSignal.INDEXING_SUCCESSFULLY.value,
        "product_id": product_id,
        "indexed": indexed_count == 1
    }

#upload prodcut_search_index
@product_router.post("/upload_productsearchindex")
async def upload_productsearchindex(request: Request):

    product_model = await ProductModel.create_instance(request.app.vector_db_client.db_client)
    catalog_controller = CatalogController(
        vectordb_client = request.app.vector_db_client, 
        embedding_client = request.app.embedding_client, 
        generation_client = request.app.generation_client,
        product_model = product_model
    )

    indexed_count = await catalog_controller.index_all_products()

    return {
        "message": ResponseSignal.INDEXED_SUCCESSFULLY.value,
        "indexed_products": indexed_count
    }

## search product
@product_router.get("/search_product")
async def search_product(request: Request, search_product:SearchProduct):

    product_model = await ProductModel.create_instance(request.app.vector_db_client.db_client)
    catalog_controller = CatalogController(
        vectordb_client = request.app.vector_db_client, 
        embedding_client = request.app.embedding_client, 
        generation_client = request.app.generation_client,
        product_model = product_model
    )
    results = []
    try:
        results = await catalog_controller.hybrid_search(query=search_product.query, limit=search_product.limit, **search_product.filters)
    except Exception:
        logging.getLogger("uvicorn").exception(
            "error searching product",
        )

    return {
        "message":ResponseSignal.SEARCH_SUCCESSFULLY.value,
        "results":results
    }