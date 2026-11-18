FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y docker.io python3 python3-venv python3-pip && rm -rf /var/lib/apt/lists/*
