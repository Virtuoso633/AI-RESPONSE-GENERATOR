# Add content to frontend/utils.py
import requests
from typing import Dict, List, Any
import json

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """
    Helper function to call the backend API
    
    Args:
        endpoint: API endpoint to call
        method: HTTP method (GET, POST, etc.)
        data: Data to send in the request body
        
    Returns:
        API response as dictionary
    """
    try:
        if method.upper() == "GET":
            response = requests.get(endpoint)
        elif method.upper() == "POST":
            response = requests.post(endpoint, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from API"}
