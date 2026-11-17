from locust import HttpUser, task, between
import random

class PeakDeliveryUser(HttpUser):
    # Simulate users clicking fast, waiting only 0.1 to 0.5 seconds between clicks
    wait_time = between(0.1, 0.5)

    @task
    def place_order(self):
        # The new randomized menu
        menu = ["Chicken Biryani", "Butter Paneer", "Garlic Naan", "Diet Coke"]
        
        self.client.post("/place_order", json={
            "user_id": random.randint(1, 100000),
            "item_name": random.choice(menu),
            "price": random.choice([250.0, 180.0, 40.0, 60.0]),
            "is_vip": random.choice([True, False])
        })