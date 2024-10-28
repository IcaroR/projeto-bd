from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import json

router = APIRouter()

conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port="5432")


@router.get("/products")
async def read_products():
    try:
        cursor = conn.cursor()
        info = cursor.execute("SELECT * FROM products")
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Error retrieving products"}))
    return JSONResponse(content=json.dumps(info))


@router.post("/products")
async def add_product(name: str, price: float, quantity: int, seller_id: int, fab_at: str):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, quantity, seller_id, fab_at) VALUES (%s, %s, %s, %s)", (name, price, quantity, seller_id, fab_at))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Product already exists"}))
    return JSONResponse(content=json.dumps({"message": "Product added"}))


@router.delete("/products")
async def remove_product(item_id: int, seller_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE item_id = %s AND seller_id = %s", (item_id, seller_id))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Product not found"}))
    return JSONResponse(content=json.dumps({"message": "Product removed"}))


@router.put("/products")
async def update_quantity(item_id: int, seller_id: int, quantity: int):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET quantity = %s WHERE item_id = %s AND seller_id = %s", (quantity, item_id, seller_id))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Product not found"}))
    return JSONResponse(content=json.dumps({"message": "Quantity updated"}))