import random
from datetime import datetime, timedelta
import requests

BASE_URL = "http://localhost:8000"

class APIClient:

    @staticmethod
    def get_kpis():
        response = requests.get(f"{BASE_URL}/dashboard/kpis")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_delayed_orders():
        response = requests.get(
            f"{BASE_URL}/delayed-orders"
        )
        response.raise_for_status()
        return response.json() 
    
    @staticmethod
    def get_delay_forecast():
        try:
            response = requests.get(
                f"{BASE_URL}/forecast/delayed-orders"
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Forecast API Error: {e}")

            return {
                "history": [],
                "forecast": []
            }


    @staticmethod
    def send_chat_query(query_text: str, session_id: str):

        payload = {
        "query": query_text,
        "session_id": session_id
    }

        try:
            response = requests.post(
                f"{BASE_URL}/agents/query",
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": str(e)
            }  
        
    @staticmethod
    def get_complaints_by_category():
        response = requests.get(
            f"{BASE_URL}/dashboard/charts/complaints"
        )
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_live_agent_status():
        try:
            response = requests.get(
                f"{BASE_URL}/agents/status"
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching live agent status: {e}")
        
        # Fallback to empty list or mock data if API fails
        return []
    
    
    
class MockAPIClient:

    @staticmethod
    def get_delayed_order_trend():

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        values = [
            random.randint(150, 700)
            for _ in range(7)
        ]

        return {
            "days": days,
            "values": values
        }


    @staticmethod
    def get_sla_data():

        return {
            "days":
                ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],

            "values":
                [random.randint(10,60) for _ in range(7)]
        }


    @staticmethod
    def get_notifications():

        return [
            {
                "title":"Critical Inventory Alert",
                "priority":"High"
            },
            {
                "title":"Refund SLA Breach",
                "priority":"Medium"
            },
            {
                "title":"Delayed Shipment Spike",
                "priority":"High"
            }
        ]