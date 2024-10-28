from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import json

router = APIRouter()

conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port="5432")

@router.get("/users/{user_id}")
async def read_user(user_id: int):
    cursor = conn.cursor()
    info = cursor.execute("SELECT * FROM users WHERE user_id = %s", user_id)
    conn.commit()
    return JSONResponse(content=json.dumps(info))


@router.get("/users")
async def read_users():
    cursor = conn.cursor()
    info = cursor.execute("SELECT * FROM users")
    conn.commit()
    return JSONResponse(content=json.dumps(info))


@router.post("/users")
async def add_user(name: str, email: str, password: str, address: str, one_piece: bool):
    try:
        cursor = conn.cursor()
        # Conferindo se existe um user com o mesmo email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Inserindo usuário
        cursor.execute("INSERT INTO users (name, email, password, address, one_piece) VALUES (%s, %s, %s, %s, %s)", (name, email, password, address, one_piece))
        conn.commit()
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content=json.dumps({"message": "An error occurred"}), status_code=500)
    
    return JSONResponse(content=json.dumps({"message": "User added"}))


@router.delete("/users/{user_id}")
async def remove_user(user_id: int):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", user_id)
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "User not found"}))
    return JSONResponse(content=json.dumps({"message": "User removed"}))


@router.put("/users/{user_id}")
async def update_user(user_id: int, name: str, email: str, password: str, address: str, one_piece: bool):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        cursor.execute("UPDATE users SET name = %s, email = %s, password = %s, address = %s, one_piece = %s WHERE user_id = %s", (name, email, password, address, one_piece, user_id))
        conn.commit()
    except:
        return JSONResponse(content=json.dumps({"message": "User not found"}))
    return JSONResponse(content=json.dumps({"message": "User updated"}))