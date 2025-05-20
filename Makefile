.PHONY: build up down logs test clean

# Default target
all: build up

# Build the Docker images
build:
	docker-compose build

# Start the containers
up:
	docker-compose up -d

# Start the development containers
dev:
	docker-compose -f docker-compose.dev.yml up

# Stop the containers
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run tests
test:
	docker-compose run --rm backend pytest tests/ -v

# Clean up
clean:
	docker-compose down -v
	docker system prune -f
