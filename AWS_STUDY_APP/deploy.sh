#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AWS Study App Deployment Script ${NC}"
echo -e "${GREEN}========================================${NC}"

# Ensure we're in the correct directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo -e "${YELLOW}Working directory: $(pwd)${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Creating Docker configuration files...${NC}"

# Create Dockerfile
cat > Dockerfile << 'EOF'
# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and static assets
COPY main.py .
COPY questions.json .
COPY templates/ ./templates/
COPY static/ ./static/

# Expose the port the app runs on
EXPOSE 5019

# Command to run the application
CMD ["python", "main.py"]
EOF
echo -e "${GREEN}✓ Created Dockerfile${NC}"

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'

services:
  aws-study-app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5019:5019"
    volumes:
      # This allows the questions.json file to persist between container restarts
      - ./questions.json:/app/questions.json
    restart: unless-stopped
EOF
echo -e "${GREEN}✓ Created docker-compose.yml${NC}"

# Create .dockerignore
cat > .dockerignore << 'EOF'
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.git/
EOF
echo -e "${GREEN}✓ Created .dockerignore${NC}"

# Ensure requirements.txt has the necessary packages
if [ ! -f requirements.txt ]; then
    cat > requirements.txt << 'EOF'
Flask==2.3.3
Markdown==3.5.1
EOF
    echo -e "${GREEN}✓ Created requirements.txt${NC}"
else
    # Check if Flask and Markdown are in requirements.txt
    if ! grep -q "Flask" requirements.txt || ! grep -q "Markdown" requirements.txt; then
        echo -e "${YELLOW}Updating requirements.txt...${NC}"
        
        # Add Flask if not present
        if ! grep -q "Flask" requirements.txt; then
            echo "Flask==2.3.3" >> requirements.txt
        fi
        
        # Add Markdown if not present
        if ! grep -q "Markdown" requirements.txt; then
            echo "Markdown==3.5.1" >> requirements.txt
        fi
        
        echo -e "${GREEN}✓ Updated requirements.txt${NC}"
    else
        echo -e "${GREEN}✓ requirements.txt already contains necessary packages${NC}"
    fi
fi

# Ensure directories exist
mkdir -p templates static
echo -e "${GREEN}✓ Ensured templates and static directories exist${NC}"

# Check for questions.json
if [ ! -f questions.json ]; then
    echo -e "${YELLOW}Creating a default questions.json file...${NC}"
    
    cat > questions.json << 'EOF'
[
    {
        "id": 1,
        "question": "Which AWS service is primarily used for storing static files?",
        "options": ["EC2", "S3", "DynamoDB", "RDS"],
        "correct_answer": "S3",
        "explanation": "Amazon S3 (Simple Storage Service) is an object storage service that offers industry-leading scalability, data availability, security, and performance for storing static files."
    },
    {
        "id": 2,
        "question": "Which AWS service would you use to run containers?",
        "options": ["EC2", "S3", "ECS/EKS", "Lambda"],
        "correct_answer": "ECS/EKS",
        "explanation": "Amazon ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service) are services designed specifically for running containers in AWS."
    }
]
EOF
    echo -e "${GREEN}✓ Created default questions.json${NC}"
fi

echo -e "${YELLOW}Building and starting the Docker container...${NC}"

# Stop any existing container
docker compose down

# Build and start the container
if docker compose up -d; then
    echo -e "${GREEN}✓ Docker container started successfully!${NC}"
    echo -e "${GREEN}✓ Your AWS Study App is now available at http://localhost:5019${NC}"
    
    # Get the container IP address for accessing on the local network
    CONTAINER_IP=$(hostname -I | awk '{print $1}')
    if [ ! -z "$CONTAINER_IP" ]; then
        echo -e "${GREEN}✓ You can also access it on your local network at http://${CONTAINER_IP}:5019${NC}"
    fi
else
    echo -e "${RED}Error: Failed to start Docker container. Check the logs for more information.${NC}"
    exit 1
fi

echo -e "${YELLOW}Deployment complete!${NC}"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo -e "  ${YELLOW}docker-compose logs -f${NC}        # View logs"
echo -e "  ${YELLOW}docker compose down${NC}           # Stop the app"
echo -e "  ${YELLOW}docker compose up -d${NC}          # Start the app"
echo -e "  ${YELLOW}docker-compose restart${NC}        # Restart the app"