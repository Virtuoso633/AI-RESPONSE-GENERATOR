import pytest
from unittest.mock import MagicMock, patch
from app.ai_service import AIService # Assuming your AIService is in app.ai_service

@pytest.fixture
def ai_service():
    with patch('app.ai_service.Groq') as mock_groq:
        # Mock the Groq client instance and its methods if necessary
        mock_client_instance = MagicMock()
        mock_groq.return_value = mock_client_instance
        service = AIService()
        service.client = mock_client_instance # Ensure the service uses the mocked client
        return service

def test_generate_casual_response_prompt_formatting(ai_service):
    query = "What is Python?"
    expected_prompt_content = f"You are a friendly and casual assistant. Explain this in a conversational, easy-to-understand way: {query}"
    
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "A fun snake language!"
    ai_service.client.chat.completions.create.return_value = mock_completion

    ai_service.generate_casual_response(query)

    # Check if the create method was called
    ai_service.client.chat.completions.create.assert_called_once()
    # Get the arguments it was called with
    args, kwargs = ai_service.client.chat.completions.create.call_args
    
    # Check the user message content
    user_message = next(m for m in kwargs['messages'] if m['role'] == 'user')
    assert user_message['content'] == expected_prompt_content
    system_message = next(m for m in kwargs['messages'] if m['role'] == 'system')
    assert system_message['content'] == "You are a helpful assistant that speaks in a casual, friendly tone."
    assert kwargs['model'] == ai_service.model
    assert kwargs['temperature'] == 0.7

def test_generate_formal_response_prompt_formatting(ai_service):
    query = "Explain quantum computing."
    expected_prompt_content = f"You are a professional academic assistant. Provide a formal, detailed explanation of: {query}"

    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "Quantum computing is..."
    ai_service.client.chat.completions.create.return_value = mock_completion

    ai_service.generate_formal_response(query)
    
    ai_service.client.chat.completions.create.assert_called_once()
    args, kwargs = ai_service.client.chat.completions.create.call_args
    
    user_message = next(m for m in kwargs['messages'] if m['role'] == 'user')
    assert user_message['content'] == expected_prompt_content
    system_message = next(m for m in kwargs['messages'] if m['role'] == 'system')
    assert system_message['content'] == "You are a helpful assistant that speaks in a formal, academic tone."
    assert kwargs['model'] == ai_service.model
    assert kwargs['temperature'] == 0.3

def test_generate_responses_calls_both_methods(ai_service):
    query = "Test query"
    casual_mock_response = "Casual answer."
    formal_mock_response = "Formal answer."

    # Patch the individual generation methods within the service instance for this test
    with patch.object(ai_service, 'generate_casual_response', return_value=casual_mock_response) as mock_casual, \
         patch.object(ai_service, 'generate_formal_response', return_value=formal_mock_response) as mock_formal:
        
        result = ai_service.generate_responses(query)

        mock_casual.assert_called_once_with(query)
        mock_formal.assert_called_once_with(query)
        assert result == {
            "casual_response": casual_mock_response,
            "formal_response": formal_mock_response
        }