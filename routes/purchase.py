from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import json

router = APIRouter()

conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="localhost", port="5432")

@router.post("/purchase")
async def add_purchase(user_id: int, payment_method: str):
    try:
        cursor = conn.cursor()
        # Iniciando a transação
        conn.autocommit = False

        # Pegando todos os itens do carrinho
        cursor.execute("SELECT item_id, quantity FROM cart WHERE user_id = %s", (user_id,))
        carts = cursor.fetchall()
        if not carts:
            raise HTTPException(status_code=400, detail="Cart not found")
        
        for cart in carts:
            item_id, requested_quantity = cart

            # Pegando todos os vendedores do produto
            cursor.execute("""
                SELECT seller_id, quantity 
                FROM products 
                WHERE item_id = %s 
                ORDER BY seller_id ASC 
                FOR UPDATE
            """, (item_id,))
            
            sellers = cursor.fetchall()
            if not sellers:
                raise HTTPException(status_code=400, detail=f"Product {item_id} not found")
            
           
            # Verificando se tem a quantidade necessária de produtos
            total_available = sum(seller[1] for seller in sellers)
            if total_available < requested_quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough items for product {item_id}. Requested: {requested_quantity}, Available: {total_available}"
                )
            item_total_value = []
            # Alocando os produtos dos vendedores
            remaining = requested_quantity
            for seller in sellers:
                seller_id, seller_quantity = seller
                
                if seller_quantity >= remaining:
                    # Atualizando a quantidade do produto e reduzindo a quantidade restante
                    cursor.execute("""
                        SELECT price FROM products WHERE item_id = %s AND seller_id = %s
                    """, (item_id, seller_id))
                    info = cursor.fetchone()
                    try:
                        item_total_value.append(info[0] * seller_quantity)
                    except Exception as e:
                        print(f"ERRRO: {e}")

                    cursor.execute("""
                        UPDATE products 
                        SET quantity = quantity - %s 
                        WHERE item_id = %s AND seller_id = %s
                    """, (remaining, item_id, seller_id))
                    remaining = 0
                    break # Caso tenha alocado todos os produtos, não precisa mais percorrer os vendedores

                else:
                    # Reduzindo toda a quantidade do vendedor e reduzindo a quantidade restante
                    cursor.execute("""
                        SELECT price FROM products WHERE item_id = %s AND seller_id = %s)
                    """, (item_id, seller_id))
                    print("test")
                    item_total_value += cursor.fetchone()[0] * seller_quantity
                    cursor.execute("""
                        UPDATE products 
                        SET quantity = 0 
                        WHERE item_id = %s AND seller_id = %s
                    """, (item_id, seller_id))
                    item_total_value.append(cursor.fetchone()[0] * seller_quantity)

        print(item_total_value)
        total_price = sum(item_total_value)

        # Adicionando a compra
        cursor.execute("""
            INSERT INTO payments (user_id, payment_method, total_price) 
            VALUES (%s, %s, %s)
        """, (user_id, payment_method, total_price))

        conn.commit()
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        conn.commit()

    except HTTPException as e:
        print(e)
        conn.rollback()
        raise e
    except Exception as e:
        print(e)
        conn.rollback()
        return JSONResponse(content={"message": "An error occurred"}, status_code=500)
    finally:
        conn.autocommit = True

    return JSONResponse(content={"message": "Purchase added successfully"}, status_code=200)