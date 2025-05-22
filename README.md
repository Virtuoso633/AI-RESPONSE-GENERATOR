# AI Response Generator

An AI-powered web prototype that:
- Accepts user input
- Generates AI-based responses (casual and formal) using prompt engineering with Groq API
- Stores all interactions in a PostgreSQL database via a Python microservice
- Presents responses and history via a Streamlit UI

## Live Demo (Hosted on Render)

-   **Frontend (Streamlit UI):** [https://ai-response-frontend.onrender.com](https://ai-response-frontend.onrender.com)
-   **Backend API Base URL:** [https://ai-response-generator-2gkd.onrender.com](https://ai-response-generator-2gkd.onrender.com)
    -   API Docs (Swagger UI): [https://ai-response-generator-2gkd.onrender.com/docs](https://ai-response-generator-2gkd.onrender.com/docs)

*(Note: Free tier services on Render may "spin down" after a period of inactivity and might take a moment to start up on the first request.)*

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

-   **Backend**: FastAPI, SQLAlchemy, Pydantic
-   **Database**: PostgreSQL
-   **AI**: Groq API (Llama 3)
-   **Frontend**: Streamlit
-   **Containerization**: Docker, Docker Compose
-   **Testing**: Pytest, Unittest.mock
-   **Hosting**: Render

## Setup and Installation (Local Development)

### Prerequisites

-   Docker and Docker Compose
-   Groq API key (sign up at [Groq](https://groq.com/))

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
    *(The `DATABASE_URL` in the `.env` file is pre-configured for the local Docker setup.)*

4.  Build and start the containers:
    ```bash
    make build
    make up
    ```
    *(This uses `docker-compose.yml` for a production-like setup where hot-reloading is not enabled by default for the backend.)*

5.  Access the application locally:
    -   Frontend: http://localhost:8501
    -   Backend API: http://localhost:8000
    -   API Docs (Swagger UI): http://localhost:8000/docs

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

-   **`POST /api/generate`**
    -   Generates casual and formal responses for a query and stores the interaction.
    -   Request body: `{ "user_id": "string", "query": "string" }`
    -   Response: `{ "casual_response": "string", "formal_response": "string" }`

-   **`GET /api/history?user_id=string`**
    -   Returns all past interactions for the given user, ordered by most recent first.
    -   Query parameter: `user_id`
    -   Response: `List[PromptResponse]` where `PromptResponse` includes `id`, `user_id`, `query`, `casual_response`, `formal_response`, `created_at`.

-   **`GET /`**
    -   Root endpoint for the API.
    -   Response: `{ "message": "Welcome to AI Response Generator API" }`

## Prompt Engineering Strategy

The application uses two distinct prompt styles to generate varied responses from the Groq API (Llama 3 model):

1.  **Casual Style**:
    -   **System Prompt**: "You are a helpful assistant that speaks in a casual, friendly tone."
    -   **User Prompt**: "You are a friendly and casual assistant. Explain this in a conversational, easy-to-understand way: {query}"
    -   **Temperature**: 0.7 (allows for more creativity and variability)
    -   **Goal**: To provide responses that are easy to grasp, conversational, and less formal.

2.  **Formal Style**:
    -   **System Prompt**: "You are a helpful assistant that speaks in a formal, academic tone."
    -   **User Prompt**: "You are a professional academic assistant. Provide a formal, detailed explanation of: {query}"
    -   **Temperature**: 0.3 (encourages more focused and deterministic responses)
    -   **Goal**: To generate responses that are structured, detailed, and suitable for more academic or professional contexts.

The `AIService` class in `backend/app/ai_service.py` encapsulates this logic.

## Deployment on Render

The application is hosted on Render. Here's a summary of the deployment steps:

1.  **Prerequisites**:
    *   A Render account.
    *   The project code pushed to a GitHub repository.

2.  **Create PostgreSQL Database on Render**:
    *   From the Render dashboard, created a new "PostgreSQL" service.
    *   Configured a name, region, and selected the free plan.
    *   Once provisioned, copied the **"Internal Connection String"** for the database.

3.  **Deploy Backend Service (FastAPI)**:
    *   Created a new "Web Service" on Render.
    *   Connected the GitHub repository.
    *   **Configuration**:
        *   **Name**: e.g., `ai-response-backend`
        *   **Environment**: Docker
        *   **Region**: Same as the database.
        *   **Branch**: `main` (or your deployment branch).
        *   **Root Directory**: `backend` (This tells Render to use the `backend` folder as the build context).
        *   **Dockerfile Path**: `Dockerfile` (Render looks for this file within the "Root Directory").
        *   **Plan**: Free.
    *   **Environment Variables**:
        *   `DATABASE_URL`: Set to the "Internal Connection String" from the Render PostgreSQL service.
        *   `GROQ_API_KEY`: Your actual Groq API key.
        *   `PYTHONUNBUFFERED`: `1` (for better logging).
    *   After deployment, Render provided a public URL for the backend (e.g., `https://ai-response-generator-2gkd.onrender.com`).

4.  **Deploy Frontend Service (Streamlit)**:
    *   Created another "Web Service" on Render.
    *   Connected the same GitHub repository.
    *   **Configuration**:
        *   **Name**: e.g., `ai-response-frontend`
        *   **Environment**: Docker
        *   **Root Directory**: `frontend`
        *   **Dockerfile Path**: `Dockerfile`
        *   **Plan**: Free.
    *   **Environment Variables**:
        *   `API_URL`: Set to the public URL of the deployed backend service, suffixed with `/api` (e.g., `https://ai-response-generator-2gkd.onrender.com/api`).
        *   `PYTHONUNBUFFERED`: `1`.
    *   After deployment, Render provided a public URL for the frontend (e.g., `https://ai-response-frontend.onrender.com`).

5.  **Access and Test**:
    *   Opened the frontend URL in a browser to interact with the application.
    *   Used Render's "Logs" tab for troubleshooting if any issues arose.

## Challenges Faced and Solutions

During development and deployment, several challenges were encountered and resolved:

1.  **Database Connection on Startup (`psycopg2.OperationalError: Connection refused`)** (Local Docker Compose):
    -   **Challenge**: The backend service would sometimes try to connect to the PostgreSQL database before the database service within the Docker container was fully initialized.
    -   **Solution**: Implemented a `healthcheck` in the `docker-compose.dev.yml` for the `db` service using `pg_isready`. The `backend` service's `depends_on` clause was updated to `condition: service_healthy`.

2.  **Pydantic Validation Error for UUID (`ValidationError: Input should be a valid string`)**:
    -   **Challenge**: The `/api/history` endpoint was returning a 500 Internal Server Error due to a type mismatch between SQLAlchemy `UUID` and Pydantic `str` for the `id` field.
    -   **Solution**: A `@field_validator("id", mode='before')` was added to the `PromptResponse` Pydantic model to explicitly convert `UUID` to `str` before validation.

3.  **SQLite UUID Incompatibility During Testing (`sqlalchemy.exc.CompileError: ...can't render element of type UUID`)**:
    -   **Challenge**: Tests using an in-memory SQLite database failed because SQLite doesn't natively support UUID types.
    -   **Solution**: Implemented a custom SQLAlchemy `TypeDecorator` (`SQLiteUUID`) and an event listener in `backend/tests/test_api.py` to handle UUIDs as strings in SQLite during tests.

4.  **Pytest Fixture Not Found (`fixture 'mock_generate' not found`)**:
    -   **Challenge**: Some API validation tests incorrectly expected a `mock_generate` fixture.
    -   **Solution**: Removed the unused fixture parameter from these tests. For tests where the service call was expected (e.g., empty but valid query), an explicit `with patch(...)` was used.

5.  **Docker Test Environment Path Issue (`ERROR: file or directory not found: tests/`)**:
    -   **Challenge**: `pytest` couldn't find the `tests/` directory due to a volume mount mismatch in `docker-compose.yml`.
    -   **Solution**: Corrected the `backend` service volume mount in `docker-compose.yml` to ` ./backend:/code`.

6.  **Render Deployment: Dockerfile Not Found**:
    -   **Challenge**: Render initially couldn't find the Dockerfiles because they are nested within `backend/` and `frontend/` subdirectories.
    -   **Solution**: For each Render service (backend and frontend), configured the **"Root Directory"** to the respective subdirectory (e.g., `backend`) and set the **"Dockerfile Path"** to `Dockerfile`.

7.  **Render Deployment: Database Hostname Resolution (`could not translate host name "db"`)**:
    -   **Challenge**: The deployed backend on Render failed to connect to the database because it was trying to use the hostname `db` (from the local `DATABASE_URL` used with Docker Compose).
    -   **Solution**: Ensured the `DATABASE_URL` environment variable for the backend service on Render was correctly set to the **"Internal Connection String"** provided by Render's managed PostgreSQL service.

## License

MIT
