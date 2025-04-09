#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u

# --- Configuration ---

REPO_URL="https://github.com/Qbizinc/airflow3-sandbox-data-pipeline.git"
# Extract repository name to determine the directory name after cloning
# This attempts to get the name like 'my-repo' from 'https://github.com/user/my-repo.git'
REPO_DIR=$(basename "$REPO_URL" .git)

# --- Script Start ---
echo "Starting EC2 setup for Docker Compose project..."

echo "Updating system packages..."
sudo yum update -y

echo "Installing Git..."
sudo yum install git -y

echo "Installing Docker..."
sudo yum install docker -y

echo "Starting and enabling Docker service..."
sudo systemctl start docker
sudo systemctl enable docker
echo "Docker service started and enabled."

# This allows running docker commands without sudo.
# IMPORTANT: This change takes effect after you log out and log back in,
# or by running 'newgrp docker' in the current shell (may require password).
echo "Adding ec2-user to the docker group..."
sudo usermod -a -G docker ec2-user
echo "User 'ec2-user' added to 'docker' group. Log out and log back in for changes to take effect."

echo "Installing Docker Compose manually..."

DOCKER_COMPOSE_VERSION="v2.26.1"

DOCKER_CONFIG=${DOCKER_CONFIG:-/usr/local/lib/docker}
INSTALL_DIR="$DOCKER_CONFIG/cli-plugins"
INSTALL_PATH="$INSTALL_DIR/docker-compose"

echo "Creating directory $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"

# Download the Docker Compose binary
echo "Downloading Docker Compose version ${DOCKER_COMPOSE_VERSION}..."
sudo curl -SL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" -o "$INSTALL_PATH"

echo "Making Docker Compose binary executable..."
sudo chmod +x "$INSTALL_PATH"

echo "Docker Compose installed manually to $INSTALL_PATH."

# Verify installation
echo "Verifying Docker Compose installation..."
docker compose version
if [ $? -ne 0 ]; then
    echo "Docker Compose installation verification failed. Please check the steps."
    exit 1
fi
echo "Docker Compose verification successful."

echo "Cloning repository from $REPO_URL..."
cd /home/ec2-user
# Check if directory already exists (e.g., from a previous run)
if [ -d "$REPO_DIR" ]; then
  echo "Directory $REPO_DIR already exists. Skipping clone."
else
  git clone "$REPO_URL"
  echo "Repository cloned."
fi

echo "Changing directory to $REPO_DIR..."
cd "/home/ec2-user/$REPO_DIR"

# --- Script End ---
echo "---------------------------------------------------------------------"
echo "Setup script finished!"
echo "Repository cloned into: /home/ec2-user/$REPO_DIR"
echo "IMPORTANT: Log out and log back in for docker group permissions to apply."
echo "After logging back in, navigate to /home/ec2-user/$REPO_DIR and run:"
echo "  docker compose up -d"
echo "To check running containers: docker ps"
echo "To view logs: docker compose logs -f"
echo "---------------------------------------------------------------------"
