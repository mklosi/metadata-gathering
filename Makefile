# Define the Docker image name and version tag
BASE_NAME=wmt-martin-klosi-file-metadata
IMAGE_NAME=$(BASE_NAME)
IMAGE_TAG=0.0.1
FULL_IMAGE_NAME=$(IMAGE_NAME):$(IMAGE_TAG)
CONTAINER_NAME=$(BASE_NAME)-container

# Define the poetry export and build commands
.PHONY: build run requirements

# Export requirements.txt using poetry
requirements:
	poetry install --sync
	poetry export --without-hashes --format=requirements.txt > server/requirements.txt

# Build the Docker image
build: requirements
	docker build -t $(FULL_IMAGE_NAME) .

# Run the Docker container
run:
	@docker stop $(CONTAINER_NAME) > /dev/null || true
	@docker rm $(CONTAINER_NAME) > /dev/null || true
	docker run --name $(CONTAINER_NAME) -p 4000:4000 $(FULL_IMAGE_NAME)
