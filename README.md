# AI Response Generator

An AI-powered web prototype that:
- Accepts user input
- Generates AI-based responses (casual and formal) using prompt engineering with Groq API
- Stores all interactions in a PostgreSQL database via a Python microservice
- Presents responses and history via a Streamlit UI

## Project Structure

```
ai-response-generator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── ai_service.py
│   │   └── routes.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_ai_service.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run_tests.sh
├── frontend/
│   ├── app.py
│   ├── utils.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env
├── .env.example
├── .dockerignore
├── Makefile
└── README.md
```

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL
- **AI**: Groq API (Llama 3)
- **Frontend**: Streamlit
- **Containerization**: Docker, Docker Compose
- **Testing**: Pytest, Unittest.mock

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Groq API key (sign up at [Groq](https://groq.com/))

### Quick Start

1.  Clone the repository:
    ```bash
    git clone https://github.com/Virtuoso633/AI-RESPONSE-GENERATOR.git
    cd ai-response-generator
    ```

2.  Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```

3.  Add your Groq API key to the `.env` file:
    ```
    GROQ_API_KEY=your_groq_api_key_here
    ```
    *(The `DATABASE_URL` is pre-configured for the Docker setup.)*

4.  Build and start the containers:
    ```bash
    make build
    make up
    ```
    *(This uses `docker-compose.yml` for a production-like setup where hot-reloading is not enabled by default for the backend.)*

5.  Access the application:
    - Frontend: http://localhost:8501
    - Backend API: http://localhost:8000
    - API Docs (Swagger UI): http://localhost:8000/docs

### Development Mode

To run the application in development mode with hot reloading for both backend and frontend:

```bash
make dev
```
This uses `docker-compose.dev.yml`.

### Running Tests

To run the backend unit and integration tests:

```bash
make test
```

### Stopping the Application

```bash
make down
```
To stop and remove volumes (like the database data):
```bash
make clean
```

## API Endpoints

- **`POST /api/generate`**
  - Generates casual and formal responses for a query and stores the interaction.
  - Request body: `{ "user_id": "string", "query": "string" }`
  - Response: `{ "casual_response": "string", "formal_response": "string" }`

- **`GET /api/history?user_id=string`**
  - Returns all past interactions for the given user, ordered by most recent first.
  - Query parameter: `user_id`
  - Response: `List[PromptResponse]` where `PromptResponse` includes `id`, `user_id`, `query`, `casual_response`, `formal_response`, `created_at`.

- **`GET /`**
  - Root endpoint for the API.
  - Response: `{ "message": "Welcome to AI Response Generator API" }`

## Prompt Engineering Strategy

The application uses two distinct prompt styles to generate varied responses from the Groq API (Llama 3 model):

1.  **Casual Style**:
    - **System Prompt**: "You are a helpful assistant that speaks in a casual, friendly tone."
    - **User Prompt**: "You are a friendly and casual assistant. Explain this in a conversational, easy-to-understand way: {query}"
    - **Temperature**: 0.7 (allows for more creativity and variability)
    - **Goal**: To provide responses that are easy to grasp, conversational, and less formal.

2.  **Formal Style**:
    - **System Prompt**: "You are a helpful assistant that speaks in a formal, academic tone."
    - **User Prompt**: "You are a professional academic assistant. Provide a formal, detailed explanation of: {query}"
    - **Temperature**: 0.3 (encourages more focused and deterministic responses)
    - **Goal**: To generate responses that are structured, detailed, and suitable for more academic or professional contexts.

The `AIService` class in `backend/app/ai_service.py` encapsulates this logic.

## Challenges Faced and Solutions

During development, several challenges were encountered and resolved:

1.  **Database Connection on Startup (`psycopg2.OperationalError: Connection refused`)**:
    - **Challenge**: The backend service would sometimes try to connect to the PostgreSQL database before the database service within the Docker container was fully initialized and ready to accept connections.
    - **Solution**: Implemented a `healthcheck` in the `docker-compose.dev.yml` for the `db` service using `pg_isready`. The `backend` service's `depends_on` clause was updated to `condition: service_healthy`, ensuring it waits for the database to be fully operational.

2.  **Pydantic Validation Error for UUID (`ValidationError: Input should be a valid string`)**:
    - **Challenge**: The `/api/history` endpoint was returning a 500 Internal Server Error. The SQLAlchemy model used `UUID` for the `id` field, while the Pydantic response model `PromptResponse` expected a `str`. The automatic coercion was not happening as expected during serialization.
    - **Solution**: A `@field_validator("id", mode='before')` was added to the `PromptResponse` Pydantic model in `backend/app/routes.py`. This validator explicitly converts the `UUID` object to its string representation *before* Pydantic's standard validation occurs, resolving the type mismatch.

3.  **SQLite UUID Incompatibility During Testing (`sqlalchemy.exc.CompileError: ...can't render element of type UUID`)**:
    - **Challenge**: Unit and integration tests for the API (using an in-memory SQLite database for speed and isolation) failed because SQLite doesn't have a native UUID type, unlike PostgreSQL.
    - **Solution**:
        - A custom SQLAlchemy `TypeDecorator` (`SQLiteUUID`) was created in `backend/tests/test_api.py`. This decorator handles the conversion of Python `uuid.UUID` objects to strings (`CHAR(36)`) when writing to SQLite and back to `uuid.UUID` objects when reading.
        - An SQLAlchemy event listener (`@event.listens_for(Base.metadata, "before_create")`) was implemented. This listener dynamically changes the column type from `postgresql.UUID` to the custom `SQLiteUUID` if the dialect is SQLite, just before tables are created for the test session.

4.  **Pytest Fixture Not Found (`fixture 'mock_generate' not found`)**:
    - **Challenge**: Some API validation tests in `backend/tests/test_api.py` were incorrectly defined to accept a `mock_generate` fixture that wasn't applied to them via a `@patch` decorator.
    - **Solution**: The unused `mock_generate` parameter was removed from the definitions of these specific test functions, as the mock was not needed for tests that should fail input validation before the service call is made. For the `test_generate_endpoint_invalid_payload_empty_query` (where an empty string is valid by Pydantic default), an explicit `with patch(...)` was added to clarify its behavior and mock the service call.

5.  **Docker Test Environment Path Issue (`ERROR: file or directory not found: tests/`)**:
    - **Challenge**: The `make test` command initially failed because `pytest` couldn't find the `tests/` directory. This was due to an incorrect volume mount path in the main `docker-compose.yml` (`./backend:/app`) conflicting with the `WORKDIR /code` in the `backend/Dockerfile`.
    - **Solution**: The volume mount in `docker-compose.yml` for the `backend` service was corrected to ` ./backend:/code`, aligning it with the `WORKDIR` and the `docker-compose.dev.yml` configuration.

## License

MIT
```
