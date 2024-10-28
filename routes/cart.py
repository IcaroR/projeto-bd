from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import json

router = APIRouter()

conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port="5432")


@router.get("/cart/{user_id}")
async def read_cart(user_id: int):
    cursor = conn.cursor()
    info = cursor.execute("SELECT * FROM cart WHERE user_id = %s", (user_id,))
    conn.commit()
    return JSONResponse(content=json.dumps(info))


@router.post("/cart/{user_id}")
async def add_item(user_id: int, item_id: int, quantity: int):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cart (user_id, item_id, quantity) VALUES (%s, %s, %s)", (user_id, item_id, quantity))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Item already in cart"}))
    return JSONResponse(content=json.dumps({"message": "Item added to cart"}))


@router.delete("/cart/{user_id}")
async def remove_item(user_id: int, item_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cart WHERE user_id = %s AND item_id = %s", (user_id, item_id))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Item not found in cart"}))
    return JSONResponse(content=json.dumps({"message": "Item removed from cart"}))


@router.put("/cart/{user_id}")
async def update_quantity(user_id: int, item_id: int, quantity: int):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND item_id = %s", (quantity, user_id, item_id))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "Item not found in cart"}))
    return JSONResponse(content=json.dumps({"message": "Quantity updated"}))