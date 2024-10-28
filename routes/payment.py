from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import json

router = APIRouter()

conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port="5432")


@router.post("/payment/{user_id}")
async def pay(user_id: int, payment_method: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM cart WHERE user_id = %s", (user_id,))
    cart = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchall()
    if len(user) == 0:
        return JSONResponse(status_code=404, content={"error": "User not found"})
    if len(cart) == 0:
        return JSONResponse(status_code=404, content={"error": "Cart is empty"})
    cur.execute("INSERT INTO payments (user_id, payment_method, payment_status) VALUES (%s, %s, 'pending') RETURNING payment_id", (user_id, payment_method))
    payment_id = cur.fetchone()[0]
    cur.execute("UPDATE cart SET payment_status = 'paid', payment_id = %s WHERE user_id = %s AND payment_status = 'pending'", (payment_id, user_id))
    conn.commit()
    return JSONResponse(status_code=200, content={"message": "Payment successful"})


@router.get("/payment/{user_id}/{payment_id}")
async def get_payment(user_id: int, payment_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments WHERE user_id = %s AND payment_id = %s", (user_id, payment_id))
    payment = cur.fetchall()
    if len(payment) == 0:
        return JSONResponse(status_code=404, content={"error": "Payment not found for this user"})
    return JSONResponse(status_code=200, content={"payment": payment})


@router.get("/payment/{user_id}")
async def get_payments(user_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments WHERE user_id = %s", (user_id,))
    payment = cur.fetchall()
    if len(payment) == 0:
        return JSONResponse(status_code=404, content={"error": "Payment not found"})
    return JSONResponse(status_code=200, content={"payment": payment})


@router.delete("/payment/{user_id}/{payment_id}")
async def delete_payment(user_id: int, payment_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments WHERE user_id = %s AND payment_id = %s", (user_id, payment_id))
    payment = cur.fetchall()
    if len(payment) == 0:
        return JSONResponse(status_code=404, content={"error": "Payment not found"})
    cur.execute("DELETE FROM payment WHERE user_id = %s AND payment_id = %s", (user_id, payment_id))
    cur.execute("UPDATE cart SET payment_status = 'pending', payment_id = NULL WHERE user_id = %s AND payment_id = %s", (user_id, payment_id))
    conn.commit()
    return JSONResponse(status_code=200, content={"message": "Payment deleted"})


@router.put("/payment/{user_id}/{payment_id}")
async def update_payment(user_id: int, payment_id: int, payment_status: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM payment WHERE user_id = %s AND payment_id = %s", (user_id, payment_id))
    payment = cur.fetchall()
    if len(payment) == 0:
        return JSONResponse(status_code=404, content={"error": "Payment not found"})
    cur.execute("UPDATE payment SET payment_status = %s WHERE user_id = %s AND payment_id = %s", (payment_status, user_id, payment_id))
    conn.commit()
    return JSONResponse(status_code=200, content={"message": "Payment updated"})