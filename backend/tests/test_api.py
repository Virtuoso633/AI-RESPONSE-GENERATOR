from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

@patch("app.ai_service.AIService.generate_responses")
def test_generate_endpoint(mock_generate):
    # Mock the AI service response
    mock_generate.return_value = {
        "casual_response": "This is a casual response",
        "formal_response": "This is a formal response"
    }
    
    # Test the generate endpoint
    response = client.post(
        "/api/generate",
        json={"user_id": "test_user", "query": "test query"}
    )
    
    assert response.status_code == 200
    assert "casual_response" in response.json()
    assert "formal_response" in response.json()