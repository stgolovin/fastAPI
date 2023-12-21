from fastapi import FastAPI
from endpoints.items import router as item_router
app = FastAPI()

app.include_router(item_router, prefix="/api")
