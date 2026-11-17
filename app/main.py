from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
import redis
from app.database import engine, Base
from app import models
import hashlib
import json

models.Base.metadata.create_all(bind = engine)
app = FastAPI(title = "Peak-delivery API")

redis_client = redis.Redis(host='localhost' , port = 6379 , decode_responses=True)

class OrderRequest(BaseModel):
    user_id:int
    item_name:str
    price:float
    is_vip:bool = False

@app.post("/place_order")
def place_order(payload:OrderRequest):
    is_banned = redis_client.sismember("blacklist:users" , payload.user_id)
    if is_banned:
        raise HTTPException(status_code=403 , detail="User blacklisted")
    
    payload_string = payload.model_dump_json()
    payload_hash = hashlib.sha256(payload_string.encode()).hexdigest()
    idempotency_key = f"req_lock:{payload_hash}"
    payload_data = payload.model_dump()
    is_new_request = redis_client.set(idempotency_key ,"locked", nx=True , ex=5)

    if not is_new_request:
        raise HTTPException(status_code = 429 , detail="double order")

    inventory_key = f"inventory:{payload.item_name}"
    item_left = redis_client.decr(inventory_key)
    if item_left <0 :
        redis_client.incr(inventory_key)
        raise HTTPException(status_code = 400 , detail="item out of stock")


    if payload.is_vip:
        redis_client.lpush("queue:vip", payload_string)
    else:
        redis_client.lpush("queue:regular" , payload_string)
    return {
        "message":"order_placed"
    }
        