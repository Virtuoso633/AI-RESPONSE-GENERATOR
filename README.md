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
│   │   └── test_api.py
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
├── .env.example
├── .dockerignore
├── Makefile
└── README.md
```

## Technologies Used

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **AI**: Groq API
- **Frontend**: Streamlit
- **Containerization**: Docker

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Groq API key

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/Virtuoso633/AI-RESPONSE-GENERATOR.git
   cd ai-response-generator
   ```

2. Create a .env file from the example:
   ```bash
   cp .env.example .env
   ```

3. Add your Groq API key to the .env file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Build and start the containers:
   ```bash
   make build
   make up
   ```

5. Access the application:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

### Development Mode

To run the application in development mode with hot reloading:

```bash
make dev
```

### Running Tests

```bash
make test
```

### Stopping the Application

```bash
make down
```

## API Endpoints

- **POST /api/generate**
  - Generates casual and formal responses for a query
  - Request body: `{ "user_id": "abc123", "query": "Explain blockchain" }`
  - Response: `{ "casual_response": "...", "formal_response": "..." }`

- **GET /api/history?user_id=abc123**
  - Returns all past interactions for the given user
  - Query parameter: user_id

## Prompt Engineering Strategy

The application uses two different prompt styles:

1. **Casual Style**: Friendly, conversational tone with simplified explanations
2. **Formal Style**: Academic, detailed explanations with technical terminology

## License

MIT
