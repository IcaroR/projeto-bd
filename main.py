from fastapi import FastAPI, APIRouter
from routes import (
    cart, 
    products, 
    users, 
    payment,
    seller,
    purchase
)

app = FastAPI()

app.include_router(cart, prefix="/cart", tags=["cart"])
app.include_router(products, prefix="/products", tags=["products"])
app.include_router(users, prefix="/users", tags=["users"])
app.include_router(payment, prefix="/payment", tags=["payment"])
app.include_router(purchase, prefix="/purchase", tags=["purchase"])
app.include_router(seller, prefix="/seller", tags=["seller"])