FROM ubuntu:22.04

# Set environment to prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install curl first
RUN apt-get update && apt-get install -y curl gnupg 

# Update package list and install basic required packages
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y \
    build-essential \
    libssl-dev \
    python3 \
    python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory and copy requirements
WORKDIR /app
COPY ./requirements.txt /app

# Upgrade pip and install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source files
# COPY . /app

# Set working directory for source files
EXPOSE 80