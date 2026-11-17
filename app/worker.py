from app.database import Session_local
import redis
import json
import time
from app.database import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
redis_client = redis.Redis(host="localhost" , port = '6379' , decode_responses=True,health_check_interval=30)

def process_worker():
    print("Listening for orders")
    while(True):
        result = redis_client.brpop(["queue:vip" , "queue:regular"] , timeout = 1)

        if result:
            queue_name , order_json = result
            order_data = json.loads(order_json)
            print(f"[{queue_name}] Processing order for User {order_data['user_id']}: {order_data['item_name']}")
            db = Session_local()
            try:
                db.execute(text("INSERT INTO orders (user_id, item_name, price) VALUES (:user_id, :item_name, :price)"),
                    {"user_id": order_data['user_id'], "item_name": order_data['item_name'], "price": order_data['price']})
                db.commit()
                print("Successfully saved to PostgreSQL.\n")
            except Exception as e:
                db.rollback()
                print(f"Database error: {e}")
                redis_client.lpush("queue:dead_letter", order_json)
                print("Order moved to Dead Letter Queue for manual review.\n")
            finally:
                db.close()


if __name__ == "__main__":
    process_worker()