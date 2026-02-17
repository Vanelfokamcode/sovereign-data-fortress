# terraform/outputs.tf
# Output values after infrastructure creation

output "postgres_connection" {
  description = "PostgreSQL connection details"
  value = {
    host     = "localhost"
    port     = var.postgres_port
    database = var.postgres_db
    user     = var.postgres_user
  }
  sensitive = true
}

output "minio_console_url" {
  description = "MinIO web console URL"
  value       = "http://localhost:${var.minio_console_port}"
}

output "minio_api_endpoint" {
  description = "MinIO API endpoint"
  value       = "localhost:${var.minio_api_port}"
}

output "network_name" {
  description = "Docker network name"
  value       = docker_network.fortress_network.name
}

output "containers_status" {
  description = "Status of deployed containers"
  value = {
    postgres = docker_container.postgres.name
    minio    = docker_container.minio.name
  }
}

# Ajoute à la fin de outputs.tf

output "localstack_endpoint" {
  description = "LocalStack AWS endpoint"
  value       = "http://localhost:${var.localstack_port}"
}

output "aws_simulation_services" {
  description = "Simulated AWS services"
  value       = var.aws_services
}
