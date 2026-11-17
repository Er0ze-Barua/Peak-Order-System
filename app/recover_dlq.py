from sqlalchemy import true
from asyncio import exceptions
from contextlib import redirect_stderr
import redis
import json
from app.database import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import time

redis_client = redis.Redis(host="localhost" , port = 6379 , decode_responses=True)
SessionLocal = sessionmaker(autocommit = False , autoflush=False , bind = engine)

def recover_failed_orders():
    print("Checking DLQ")
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        print("DB is healthy, draining dlq")
    except Exception as e:
        print("Database is still down, exiting recovery script")
        db.close()
        return
    
    while True:
        order_json = redis_client.rpop("queue:dead_letter")

        if not order_json:
            print("DLQ is empty, all resolved")
            break
        order_data = json.loads(order_json)
        print(f"Rescuing order for User {order_data['user_id']}...")
        
        try:
            db.execute(
                text("INSERT INTO orders (user_id, item_name, price) VALUES (:user_id, :item_name, :price)"),
                {"user_id": order_data['user_id'], "item_name": order_data['item_name'], "price": order_data['price']}
            )
            db.commit()
            print("Successfully saved to database.")
        except Exception as e:
            db.rollback()
            print(f"Failed to rescue order: {e}")
            redis_client.lpush("queue:dead_letter", order_json)
            break 
            
    db.close()

if __name__ == "__main__":
    print("Starting DLQ Recovery Cron Job...")
    while True:
        recover_failed_orders()
        print("Sleeping for 15 seconds...\n")
        time.sleep(15)