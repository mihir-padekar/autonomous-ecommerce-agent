import requests
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

class WorkflowService:
    @staticmethod
    def get_real_workflow_history():
        """Fetches live workflow data from the local API endpoint."""
        try:
            response = requests.get(f"{BASE_URL}/workflows/history")
            response.raise_for_status()  
            api_data = response.json()
            
            records = []
            for item in api_data:
                # Format the ISO timestamp to a readable view string
                # e.g., '2026-06-18T05:09:21.548733' -> '18-Jun-2026 05:09 AM'
                started_at_str = item.get("started_at")
                formatted_time = ""
                if started_at_str:
                    try:
                        # Clean up fractional seconds if necessary
                        dt = datetime.fromisoformat(started_at_str.split(".")[0])
                        formatted_time = dt.strftime("%d-%b-%Y %I:%M %p")
                    except Exception:
                        formatted_time = started_at_str

                # Format the duration cleanly
                duration = item.get("duration_seconds")
                duration_str = f"{round(duration, 2)} sec" if duration is not None else "In Progress"

                records.append({
                    "Workflow ID": item.get("workflow_id"),
                    "Workflow Name": item.get("workflow_name", "").replace("_", " ").title(),
                    "User Query": item.get("user_query"),
                    "Status": item.get("status"),
                    "Executed At": formatted_time,
                    "Duration": duration_str
                })
            return records

        except requests.exceptions.RequestException as e:
            # Fallback handling or display an error
            return [{"Error": "Could not connect to API server", "Details": str(e)}]

    @staticmethod
    def get_workflow_details(workflow_id: str):
        """Fetches the step-by-step agent execution breakdown for a single workflow ID."""
        try:
            response = requests.get(f"{BASE_URL}/workflows/{workflow_id}")
            if response.status_code == 404:
                return {"NotFound": True}
                
            response.raise_for_status()
            api_data = response.json()
            
            records = []
            for item in api_data:
                # Format timestamps cleanly
                ts_str = item.get("timestamp")
                formatted_ts = ""
                if ts_str:
                    try:
                        dt = datetime.fromisoformat(ts_str.split(".")[0])
                        formatted_ts = dt.strftime("%d-%b-%Y %I:%M:%S %p")
                    except Exception:
                        formatted_ts = ts_str

                records.append({
                    "Agent Name": item.get("agent_name"),
                    "Action Taken": item.get("action"),
                    "Status": item.get("status"),
                    "Execution Time": f"{item.get('execution_time', 0)}s",
                    "Timestamp": formatted_ts
                })
            return records
        except requests.exceptions.RequestException as e:
            return [{"Error": "Could not connect to API server", "Details": str(e)}]
        

    @staticmethod
    def refund_complaints_data():
        return [{"Complaint ID": f"RC{random.randint(1000,9999)}", "Customer": f"Customer {i}", "Amount": f"${random.randint(20,500)}", "Status": random.choice(["Open", "Investigating", "Closed"])} for i in range(25)]