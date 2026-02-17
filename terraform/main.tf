# terraform/main.tf
# Sovereign Data Fortress - Infrastructure as Code

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

# Configure Docker provider
provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Create a private network for all containers
resource "docker_network" "fortress_network" {
  name = "${var.project_name}-network"
  
  labels {
    label = "project"
    value = var.project_name
  }
}

# PostgreSQL Container
resource "docker_image" "postgres" {
  name = "postgres:15-alpine"
}

resource "docker_container" "postgres" {
  name  = "${var.project_name}-postgres"
  image = docker_image.postgres.image_id
  
  env = [
    "POSTGRES_USER=${var.postgres_user}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.postgres_db}"
  ]
  
  ports {
    internal = 5432
    external = var.postgres_port
  }
  
  volumes {
    host_path      = abspath("${path.module}/../data/postgres")
    container_path = "/var/lib/postgresql/data"
  }
  
  networks_advanced {
    name = docker_network.fortress_network.name
  }
  
  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.postgres_user}"]
    interval = "10s"
    timeout  = "5s"
    retries  = 5
  }
  
  restart = "unless-stopped"
  
  labels {
    label = "project"
    value = var.project_name
  }
}

# MinIO Container
resource "docker_image" "minio" {
  name = "minio/minio:latest"
}

resource "docker_container" "minio" {
  name    = "${var.project_name}-minio"
  image   = docker_image.minio.image_id
  command = ["server", "/data", "--console-address", ":9001"]
  
  env = [
    "MINIO_ROOT_USER=${var.minio_root_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_root_password}"
  ]
  
  ports {
    internal = 9000
    external = var.minio_api_port
  }
  
  ports {
    internal = 9001
    external = var.minio_console_port
  }
  
  volumes {
    host_path      = abspath("${path.module}/../data/minio")
    container_path = "/data"
  }
  
  networks_advanced {
    name = docker_network.fortress_network.name
  }
  
  healthcheck {
    test     = ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval = "30s"
    timeout  = "20s"
    retries  = 3
  }
  
  restart = "unless-stopped"
  
  labels {
    label = "project"
    value = var.project_name
  }
}

# LocalStack Container (AWS Simulation)
resource "docker_image" "localstack" {
  name = "localstack/localstack:latest"
}

resource "docker_container" "localstack" {
  name  = "${var.project_name}-localstack"
  image = docker_image.localstack.image_id

  env = [
    "SERVICES=s3,sqs",
    "DEBUG=1",
    "AWS_DEFAULT_REGION=us-east-1",
    "AWS_ACCESS_KEY_ID=test",
    "AWS_SECRET_ACCESS_KEY=test",
    "LOCALSTACK_HOST=localhost"
  ]

  ports {
    internal = 4566
    external = var.localstack_port
  }

  networks_advanced {
    name = docker_network.fortress_network.name
  }

  restart = "on-failure"

  labels {
    label = "project"
    value = var.project_name
  }
}
