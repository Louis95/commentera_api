import json
import csv
import redis
from cachetools import TTLCache
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import HTTPException, status
from typing import Dict, List, Any


class CustomerConfig:
    """
    Customer configuration manager.
    """

    def __init__(self, redis_host: str, redis_port: int, refresh_rate: int = 3) -> None:
        """
        Initialize the CustomerConfig.

        :param redis_host: Redis host address.
        :param redis_port: Redis port.
        :param refresh_rate: Refresh rate in seconds.
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.refresh_rate = refresh_rate
        self.cache = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        self.scheduler = AsyncIOScheduler()

    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """
        Load customer configurations from CSV.

        :return: Dictionary containing customer information.
        """
        customer_data = {}
        with open("customers.csv", mode="r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                customer_id = row["customer_id"]
                customer_status = row["status"]
                badge_names = [
                    badge
                    for badge in row.values()
                    if badge and badge != customer_id and badge != customer_status
                ]

                customer_info = {
                    "customer_id": customer_id,
                    "status": customer_status,
                    "badges": badge_names,
                }
                customer_data[customer_id] = customer_info
        return customer_data

    def get_customer_config(self, customer_id: str) -> Dict[str, Any]:
        """
        Fetch customer configuration from Redis.

        :param customer_id: Customer ID.
        :return: Customer configuration.
        :raises HTTPException: If customer is not registered.
        """
        customer_info = self.cache.hget(customer_id, "customer_info")

        if customer_info is not None:
            customer_info_str = customer_info.decode("utf-8")
            return json.loads(customer_info_str)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unregistered customer",
            )

    def is_valid_customer_badges(self, customer_alias: str, badges: List[str]) -> bool:
        """
        Check if provided badges are valid for the customer.

        :param customer_alias: Customer alias.
        :param badges: List of badges.
        :return: True if badges are valid, else False.
        """
        customer_info = self.get_customer_config(customer_alias)
        customer_badges = customer_info.get("badges", [])

        for badge in badges:
            if badge not in customer_badges:
                return False

        return True

    def _refresh_config(self) -> None:
        """
        Refresh customer configurations and update Redis.
        """
        print("Refreshing customer configurations...")
        customer_data = self._load_config()
        # Store customer data in Redis
        for customer_id, customer_info in customer_data.items():
            self.cache.hset(
                customer_id, "customer_info", json.dumps(customer_info)
            )

    async def start_refresh_task(self) -> None:
        """
        Start the scheduled refresh task.
        """
        print("Scheduling refresh task...")
        self._refresh_config()
        self.scheduler.add_job(
            self._refresh_config, trigger="interval", seconds=self.refresh_rate
        )
        self.scheduler.start()
        print("Refresh task scheduled.")

# Usage example:
# config = CustomerConfig(redis_host="localhost", redis_port=6379, refresh_rate=5)
# asyncio.run(config.start_refresh_task())
