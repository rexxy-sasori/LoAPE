# Makefile for my-cpu-affinity-controller

# Variables
BIN_DIR := bin
CMD_DIR := cmd
PKG_DIR := pkg
CONFIG_DIR := config
DOCKER_IMAGE_PREFIX := intel-112:5000/my-cpu-affinity
GO := go
GO_BUILD_FLAGS := -v
GO_TEST_FLAGS := -v -race
GO_LDFLAGS := -w -s

# Targets
all: build

# Build all binaries
build: build-controller build-node-agent build-scheduler-plugin

# Build the controller binary
build-controller:
	@echo "Building controller..."
	@mkdir -p $(BIN_DIR)
	$(GO) build $(GO_BUILD_FLAGS) -ldflags "$(GO_LDFLAGS)" -o $(BIN_DIR)/controller ./$(CMD_DIR)/controller

# Build the node-agent binary
build-node-agent:
	@echo "Building node-agent..."
	@mkdir -p $(BIN_DIR)
	$(GO) build $(GO_BUILD_FLAGS) -ldflags "$(GO_LDFLAGS)" -o $(BIN_DIR)/node-agent ./$(CMD_DIR)/node-agent

# Build the scheduler-plugin binary
build-scheduler-plugin:
	@echo "Building scheduler-plugin..."
	@mkdir -p $(BIN_DIR)
	$(GO) build $(GO_BUILD_FLAGS) -ldflags "$(GO_LDFLAGS)" -o $(BIN_DIR)/scheduler-plugin ./$(CMD_DIR)/scheduler-plugin

# Run tests
test:
	@echo "Running tests..."
	$(GO) test $(GO_TEST_FLAGS) ./$(PKG_DIR)/...

# Clean build artifacts
clean:
	@echo "Cleaning..."
	@rm -rf $(BIN_DIR)

# Generate code (e.g., deepcopy functions)
generate:
	@echo "Generating code..."
	@./hack/codegen.sh

# Build Docker images
docker-build: docker-build-controller docker-build-node-agent docker-build-scheduler-plugin

docker-build-amd64: docker-build-controller-amd64 docker-build-node-agent-amd64 docker-build-scheduler-plugin-amd64

docker-push-amd64: docker-push-controller-amd64 docker-push-node-agent-amd64 docker-push-scheduler-plugin-amd64

# Build the controller Docker image
docker-build-controller:
	@echo "Building controller Docker image..."
	docker build -t $(DOCKER_IMAGE_PREFIX)-controller -f Dockerfile .

# Build the node-agent Docker image
docker-build-node-agent:
	@echo "Building node-agent Docker image..."
	docker build -t $(DOCKER_IMAGE_PREFIX)-node-agent -f Dockerfile.node-agent .

# Build the scheduler-plugin Docker image
docker-build-scheduler-plugin:
	@echo "Building scheduler-plugin Docker image..."
	docker build -t $(DOCKER_IMAGE_PREFIX)-scheduler-plugin -f Dockerfile.scheduler-plugin .


# Build the controller Docker image
docker-build-controller-amd64:
	@echo "Building controller Docker image (amd64)..."
	docker buildx build --platform linux/amd64 -t $(DOCKER_IMAGE_PREFIX)-controller:amd64 -f Dockerfile .

# Build the node-agent Docker image
docker-build-node-agent-amd64:
	@echo "Building node-agent Docker image (amd64..."
	docker buildx build --platform linux/amd64 -t $(DOCKER_IMAGE_PREFIX)-node-agent:amd64 -f Dockerfile.node-agent .

# Build the scheduler-plugin Docker image
docker-build-scheduler-plugin-amd64:
	@echo "Building scheduler-plugin Docker image (amd64)..."
	docker buildx build --platform linux/amd64 -t $(DOCKER_IMAGE_PREFIX)-scheduler-plugin:amd64 -f Dockerfile.scheduler-plugin .

# Build the controller Docker image
docker-push-controller-amd64:
	@echo "Building and pushing controller Docker image (amd64)..."
	docker push $(DOCKER_IMAGE_PREFIX)-controller:amd64

# Build the node-agent Docker image
docker-push-node-agent-amd64:
	@echo "Building and pushing node-agent Docker image (amd64..."
	docker push $(DOCKER_IMAGE_PREFIX)-node-agent:amd64

# Build the scheduler-plugin Docker image
docker-push-scheduler-plugin-amd64:
	@echo "pushing scheduler-plugin Docker image (amd64)..."
	docker push $(DOCKER_IMAGE_PREFIX)-scheduler-plugin:amd64

# Help
help:
	@echo "Available targets:"
	@echo "  all                                 - Build all binaries (default)"
	@echo "  build                               - Build all binaries"
	@echo "  build-controller                    - Build the controller binary"
	@echo "  build-node-agent                    - Build the node-agent binary"
	@echo "  build-scheduler-plugin              - Build the scheduler-plugin binary"
	@echo "  test                                - Run tests"
	@echo "  clean                               - Clean build artifacts"
	@echo "  generate                            - Generate code (e.g., deepcopy functions)"
	@echo "  docker-build                        - Build all Docker images"
	@echo "  docker-build-amd64                  - Build all Docker images for amd64 architecture"
	@echo "  docker-build-controller             - Build the controller Docker image"
	@echo "  docker-build-node-agent             - Build the node-agent Docker image"
	@echo "  docker-build-scheduler-plugin       - Build the scheduler-plugin Docker image"
	@echo "  docker-build-controller-amd64       - Build the controller Docker image for amd64 architecture"
	@echo "  docker-build-node-agent-amd64       - Build the node-agent Docker image for amd64 architecture"
	@echo "  docker-build-scheduler-plugin-amd64 - Build the scheduler-plugin Docker image for amd64 architecture"
	@echo "  docker-push-amd64                   - Build and push all Docker images for amd64 architecture"
	@echo "  docker-push-controller-amd64        - Build and push the controller Docker image for amd64 architecture"
	@echo "  docker-push-node-agent-amd64        - Build and push the node-agent Docker image for amd64 architecture"
	@echo "  docker-push-scheduler-plugin-amd64  - Build and push the scheduler-plugin Docker image for amd64 architecture"
	@echo "  help                                - Show this help message"

.PHONY: all build build-controller build-node-agent build-scheduler-plugin test clean generate \
        docker-build docker-build-controller docker-build-node-agent docker-build-scheduler-plugin \
        docker-build-amd64 docker-build-controller-amd64 docker-build-node-agent-amd64 docker-build-scheduler-plugin-amd64 \
        docker-push-amd64 docker-push-controller-amd64 docker-push-node-agent-amd64 docker-push-scheduler-plugin-amd64 