from fastapi import APIRouter, HTTPException
from typing import List
from models.item import Item
import json
import redis

router = APIRouter()

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@router.post("/items/")
def create_item(item: Item):
    item_data = item.dict()
    item_data['id'] = redis_client.incr('item_counter')
    redis_client.set(str(item_data['id']), json.dumps(item_data))
    return item_data

@router.get("/items/{item_id}")
def read_item(item_id: str):
    item_data = redis_client.get(item_id)

    if item_data:
        db_item = Item(**json.loads(item_data))
        return db_item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@router.get("/items/", response_model=List[Item]) 
def read_all_items():
    all_keys = redis_client.keys("*")
    items = []

    for key in all_keys:
        if key != 'item_counter':
            item_data = redis_client.get(key)
            if item_data:
                item_dict = json.loads(item_data)
                item_dict['id'] = int(key)
                db_item = Item(**item_dict)
                items.append(db_item)

    return items

@router.delete("/items/{item_id}")
def delete_item(item_id: int):
    key = str(item_id)
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail="Item not found")
    
    redis_client.delete(key)
    return {"message": "Item deleted successfully"}

@router.put("/items/{item_id}")
def update_item(item_id: int, updated_item: Item):
    key = str(item_id)
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Обновление данных в Redis
    item_data = updated_item.model_dump()
    item_data['id'] = item_id
    redis_client.set(key, json.dumps(item_data))

    return {"message": "Item updated successfully"}
