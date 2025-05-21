from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, event, TypeDecorator, CHAR
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # Keep for the model definition
from app.main import app
from app.database import Base, get_db
from app.models import Prompt
import uuid

# --- Custom UUID type for SQLite ---
# This will store UUIDs as strings in SQLite for testing
class SQLiteUUID(TypeDecorator):
    impl = CHAR(36)  # Store as a 36-character string (including hyphens)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, uuid.UUID):
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        try:
            return uuid.UUID(value)
        except (ValueError, TypeError):
            return value # Or raise an error if strict UUID format is expected

    @property
    def python_type(self):
        return uuid.UUID
    
# Setup for an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# --- Event listener to use SQLiteUUID for UUID columns on SQLite ---
@event.listens_for(Base.metadata, "before_create")
def before_create(target, connection, **kw):
    if connection.dialect.name == "sqlite":
        # Iterate over all columns in all tables
        for table in target.tables.values():
            for column in table.columns:
                if isinstance(column.type, PG_UUID):
                    # Change the type to our custom SQLiteUUID for SQLite dialect
                    column.type = SQLiteUUID()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the in-memory database before tests run
# The event listener above will modify the UUID column type for SQLite
Base.metadata.create_all(bind=engine)

# Dependency override for tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


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
        json={"user_id": "test_user_integration", "query": "test query integration"}
    )
    
    assert response.status_code == 200
    assert "casual_response" in response.json()
    assert "formal_response" in response.json()


def test_generate_endpoint_invalid_payload_missing_userid(): # Removed mock_generate
    response = client.post(
        "/api/generate",
        json={"query": "test query"} # Missing user_id
    )
    assert response.status_code == 422 # Unprocessable Entity
    assert "user_id" in response.json()["detail"][0]["loc"]

def test_generate_endpoint_invalid_payload_missing_query(): # Removed mock_generate
    response = client.post(
        "/api/generate",
        json={"user_id": "test_user"} # Missing query
    )
    assert response.status_code == 422 # Unprocessable Entity
    assert "query" in response.json()["detail"][0]["loc"]

def test_generate_endpoint_invalid_payload_empty_query(): # Removed mock_generate
    # Pydantic v2 by default considers "" a valid string.
    # If stricter validation (e.g. min_length=1) were added to the Pydantic model,
    # this test would expect 422. For now, assuming default behavior.
    # To ensure the service isn't called, we could patch it here if we wanted to be extra safe,
    # but the 422 tests above don't need it. If this were to pass through to the service,
    # then a mock would be essential.
    # For consistency, if we *did* want to mock it to ensure it's not called or to provide a dummy response:
    # @patch("app.ai_service.AIService.generate_responses")
    # def test_generate_endpoint_invalid_payload_empty_query(mock_generate_service_call):
    #    mock_generate_service_call.return_value = {"casual_response": "", "formal_response": ""}
    
    response = client.post(
        "/api/generate",
        json={"user_id": "test_user", "query": ""}
    )

    # This assumes that an empty query is processed by the endpoint if it passes Pydantic validation.
    # If the service call is made, it should be 200.
    # If you want to ensure the service is NOT called for an empty string (even if Pydantic allows it),
    # you'd need logic in your route or service, and the test would change.
    # For now, assuming it goes through and the service is called (and would be mocked if not for this test).
    # Given the other tests, it's likely this test should also not expect the service to be called
    # if the intent is to test *input validation*.
    # If an empty query is valid and should proceed, then the test is fine as is,
    # but it's not testing a *validation failure* like the others.
    # Let's assume for now that an empty query is valid and proceeds.
    # If it were to be a validation error, the status code would be 422.
    # To make this test consistent with "validation" tests, if an empty query is *undesirable*
    # and should be a 422, the Pydantic model `GenerateRequest` would need `min_length=1` for `query`.
    # Without that, Pydantic allows empty string.
    # For now, let's assume it's valid and would hit the (mocked) service.
    # To make it a pure validation test that *doesn't* hit the service, we'd need to ensure
    # the service isn't called.
    # Given the context, these are API *input* validation tests.
    # If an empty query is allowed by Pydantic, this test as written will try to call the service.
    # Let's add a mock here to be safe and explicit for this case, as it's not a 422.

    with patch("app.ai_service.AIService.generate_responses") as mock_service_call_for_empty:
        mock_service_call_for_empty.return_value = {
            "casual_response": "Casual for empty",
            "formal_response": "Formal for empty"
        }
        response = client.post(
            "/api/generate",
            json={"user_id": "test_user", "query": ""}
        )
        assert response.status_code == 200 
        assert "casual_response" in response.json()
        mock_service_call_for_empty.assert_called_once()

def test_generate_endpoint_invalid_payload_wrong_type(): # Removed mock_generate
    response = client.post(
        "/api/generate",
        json={"user_id": 123, "query": "test query"} # user_id as int instead of str
    )
    assert response.status_code == 422
    assert "user_id" in response.json()["detail"][0]["loc"]
    assert "string_type" in response.json()["detail"][0]["type"]


@patch("app.ai_service.AIService.generate_responses")
def test_generate_and_get_history_integration(mock_generate_ai):
    # --- Part 1: Generate a new prompt entry ---
    test_user_id = f"integration_user_{uuid.uuid4()}" # Unique user_id for test isolation
    test_query = "What is integration testing?"
    mock_casual_response = "It's testing things together!"
    mock_formal_response = "Integration testing is a phase in software testing..."

    mock_generate_ai.return_value = {
        "casual_response": mock_casual_response,
        "formal_response": mock_formal_response
    }

    generate_response = client.post(
        "/api/generate",
        json={"user_id": test_user_id, "query": test_query}
    )
    assert generate_response.status_code == 200
    assert generate_response.json()["casual_response"] == mock_casual_response
    assert generate_response.json()["formal_response"] == mock_formal_response

    # --- Part 2: Retrieve history for the user ---
    history_response = client.get(f"/api/history?user_id={test_user_id}")
    assert history_response.status_code == 200
    
    history_data = history_response.json()
    assert isinstance(history_data, list)
    assert len(history_data) > 0 # Expect at least one entry

    # Find the entry we just created (assuming it's the latest for this new user)
    # In a more complex scenario, you might query the test DB directly to confirm
    # or ensure the list is ordered and pick the first.
    # For this test, we assume the history is ordered by created_at desc (as in the route)
    # and this is the only entry for this unique user.
    
    # Clean up the database after each test if necessary, or ensure unique data
    # For SQLite in-memory, it's fresh for each test run if TestClient is re-instantiated
    # or tables are dropped and recreated. Here, we rely on unique user_id.

    found_entry = None
    for entry in history_data:
        if entry["query"] == test_query and entry["user_id"] == test_user_id:
            found_entry = entry
            break
    
    assert found_entry is not None
    assert found_entry["casual_response"] == mock_casual_response
    assert found_entry["formal_response"] == mock_formal_response
    assert "id" in found_entry
    assert "created_at" in found_entry

    # --- Optional: Clean up test data if not using a fully isolated in-memory DB per test ---
    # This is generally good practice if your test DB persists between test functions.
    # For SQLite in-memory with StaticPool, the DB is typically clean per test session.
    # If you were using a persistent test DB, you'd add cleanup logic here.
    # e.g., by getting a db session and deleting the created prompt.
    # db = next(override_get_db())
    # db.query(Prompt).filter(Prompt.user_id == test_user_id).delete()
    # db.commit()
    # db.close()