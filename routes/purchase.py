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
        cursor.execute("SELECT product_id, quantity, price FROM carts WHERE user_id = %s", (user_id,))
        carts = cursor.fetchall()
        if not carts:
            raise HTTPException(status_code=400, detail="Cart not found")
        
        for cart in carts:
            product_id, requested_quantity, price = cart

            # Pegando todos os vendedores do produto
            cursor.execute("""
                SELECT seller_id, quantity 
                FROM products 
                WHERE product_id = %s 
                ORDER BY seller_id ASC 
                FOR UPDATE
            """, (product_id,))
            sellers = cursor.fetchall()
            if not sellers:
                raise HTTPException(status_code=400, detail=f"Product {product_id} not found")

            # Verificando se tem a quantidade necessária de produtos
            total_available = sum(seller[1] for seller in sellers)
            if total_available < requested_quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough items for product {product_id}. Requested: {requested_quantity}, Available: {total_available}"
                )

            # Alocando os produtos dos vendedores
            remaining = requested_quantity
            for seller in sellers:
                seller_id, seller_quantity = seller
                if seller_quantity >= remaining:
                    # Atualizando a quantidade do produto e reduzindo a quantidade restante
                    cursor.execute("""
                        UPDATE products 
                        SET quantity = quantity - %s 
                        WHERE product_id = %s AND seller_id = %s
                    """, (remaining, product_id, seller_id))
                    remaining = 0
                    break # Caso tenha alocado todos os produtos, não precisa mais percorrer os vendedores
                else:
                    # Reduzindo toda a quantidade do vendedor e reduzindo a quantidade restante
                    cursor.execute("""
                        UPDATE products 
                        SET quantity = 0 
                        WHERE product_id = %s AND seller_id = %s
                    """, (product_id, seller_id))
                    remaining -= seller_quantity

        total_price = sum(cart[1] * cart[2] for cart in carts)
        # Adicionando a compra
        cursor.execute("""
            INSERT INTO payments (user_id, payment_method, total_price) 
            VALUES (%s, %s, %s)
        """, (user_id, payment_method, total_price))

        conn.commit()

        cursor.execute("DELETE FROM carts WHERE user_id = %s", (user_id,))
        conn.commit()

    except HTTPException as e:
        conn.rollback()
        raise e
    except Exception as e:
        conn.rollback()
        return JSONResponse(content={"message": "An error occurred"}, status_code=500)
    finally:
        conn.autocommit = True

    return JSONResponse(content={"message": "Purchase added successfully"}, status_code=200)