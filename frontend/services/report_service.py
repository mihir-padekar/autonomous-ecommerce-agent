import random
import pandas as pd
import requests


BASE_URL = "http://localhost:8000"

class ReportService:

    @staticmethod
    def get_dashboard_analysis():
        """Fetches live dashboard analysis from the local FastAPI backend."""
        try:
            response = requests.get(f"{BASE_URL}/reports/dashboard")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching live dashboard report: {e}")
        
        # Safe empty structure if the API fails or is unreachable
        return {
            "workflow_type": "dashboard_analysis",
            "analysis": {},
            "report": "Dashboard report currently unavailable (API Connection Error)."
        }

    @staticmethod
    def trend_analysis():

        return pd.DataFrame(
            {
                "Month":
                    [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun"
                    ],

                "Orders":
                    [
                        random.randint(
                            10000,
                            20000
                        )
                        for _ in range(6)
                    ],

                "Complaints":
                    [
                        random.randint(
                            100,
                            600
                        )
                        for _ in range(6)
                    ]
            }
        )

    @staticmethod
    def get_live_insights():
        """Fetches live unstructured metrics string recommendations from local endpoint."""
        try:
            response = requests.get(f"{BASE_URL}/insights")
            if response.status_code == 200:
                return response.json().get("insights", [])
        except Exception as e:
            print(f"Error connecting to live AI insights API: {e}")
            
        return [] 