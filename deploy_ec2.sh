#!/bin/bash
# AWS EC2 User Data Script for Video Assistant
# This script automatically installs Docker and runs your application when the EC2 instance starts.

# 1. Update and install dependencies
apt-get update
apt-get install -y git curl

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Clone the repository
git clone https://github.com/vinnnnay/video_assistant.git /home/ubuntu/video_assistant
cd /home/ubuntu/video_assistant

# 4. Create dummy .env and cookies.txt if they don't exist so Docker doesn't fail mounting
touch .env
touch cookies.txt

# 5. Build and run using Docker Compose
docker compose up -d
