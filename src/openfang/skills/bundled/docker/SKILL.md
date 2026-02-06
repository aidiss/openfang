---
name: docker
description: Manage Docker containers, images, and volumes.
homepage: https://docs.docker.com/reference/cli/docker/
metadata:
  {
    "openfang":
      {
        "emoji": "🐳",
        "requires": { "bins": ["docker"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "docker",
              "bins": ["docker"],
              "label": "Install Docker CLI (brew)",
            },
          ],
      },
  }
---

# Docker

Manage containers, images, volumes, and networks.

## Containers

### List Containers

```bash
# Running containers
docker ps

# All containers (including stopped)
docker ps -a

# Just IDs
docker ps -q
```

### Run Container

```bash
# Basic run
docker run -d --name myapp nginx

# With port mapping
docker run -d -p 8080:80 nginx

# With volume mount
docker run -d -v $(pwd):/app node:20

# Interactive shell
docker run -it ubuntu bash

# Remove after exit
docker run --rm alpine echo "hello"
```

### Container Lifecycle

```bash
# Stop
docker stop myapp

# Start
docker start myapp

# Restart
docker restart myapp

# Remove
docker rm myapp

# Force remove running
docker rm -f myapp
```

### Logs & Exec

```bash
# View logs
docker logs myapp

# Follow logs
docker logs -f myapp

# Last 100 lines
docker logs --tail 100 myapp

# Execute command in container
docker exec myapp ls /app

# Interactive shell in running container
docker exec -it myapp bash
```

## Images

```bash
# List images
docker images

# Pull image
docker pull python:3.13

# Build from Dockerfile
docker build -t myapp .

# Build with specific file
docker build -f Dockerfile.prod -t myapp:prod .

# Remove image
docker rmi nginx

# Remove unused images
docker image prune
```

## Volumes

```bash
# List volumes
docker volume ls

# Create volume
docker volume create mydata

# Inspect volume
docker volume inspect mydata

# Remove volume
docker volume rm mydata

# Remove unused volumes
docker volume prune
```

## Networks

```bash
# List networks
docker network ls

# Create network
docker network create mynet

# Connect container to network
docker network connect mynet myapp

# Inspect network
docker network inspect mynet
```

## Docker Compose

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Rebuild and start
docker compose up -d --build

# List services
docker compose ps
```

## Cleanup

```bash
# Remove all stopped containers
docker container prune

# Remove all unused data (containers, images, volumes, networks)
docker system prune -a

# Show disk usage
docker system df
```

## Inspect & Debug

```bash
# Container details
docker inspect myapp

# Resource usage
docker stats

# Container processes
docker top myapp
```
