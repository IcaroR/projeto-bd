from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import json

router = APIRouter()

conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port="5432")

@router.get("/seller/{seller_id}")
async def read_seller(seller_id: int):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sellers WHERE seller_id = %s", (seller_id,))
    info = cursor.fetchone()
    conn.commit()
    return JSONResponse(content=json.dumps(info))


@router.get("/seller")
async def read_sellers():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sellers")
    info = cursor.fetchall()
    conn.commit()
    print(info)
    return JSONResponse(content=json.dumps(info))


@router.post("/seller")
async def add_seller(name: str, email: str, password: str, address: str, one_piece: bool):
    try:
        cursor = conn.cursor()
        # Conferindo se existe um user com o mesmo email
        cursor.execute("SELECT * FROM sellers WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Seller with this email already exists")
        
        # Inserindo usuário
        cursor.execute("INSERT INTO sellers (name, email, password, address, one_piece) VALUES (%s, %s, %s, %s, %s)", (name, email, password, address, one_piece))
        conn.commit()
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content=json.dumps({"message": "An error occurred"}), status_code=500)
    
    return JSONResponse(content=json.dumps({"message": "User added"}))


@router.delete("/seller/{seller_id}")
async def remove_seller(seller_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sellers WHERE seller_id = %s", (seller_id,))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "User not found"}))
    return JSONResponse(content=json.dumps({"message": "User removed"}))


@router.put("/seller/{seller_id}")
async def update_seller(seller_id: int, name: str, email: str, password: str, address: str, one_piece: bool):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sellers WHERE email = %s", (email,))
        existing_seller = cursor.fetchone()
        if existing_seller:
            raise HTTPException(status_code=400, detail="Seller with this email already exists")
        cursor.execute("UPDATE sellers SET name = %s, email = %s, password = %s, address = %s, one_piece = %s WHERE seller_id = %s", (name, email, password, address, one_piece, seller_id))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "User not found"}))
    return JSONResponse(content=json.dumps({"message": "User updated"}))