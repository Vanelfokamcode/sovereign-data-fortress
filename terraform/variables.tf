# terraform/variables.tf
# Variable definitions for Sovereign Data Fortress

variable "project_name" {
  description = "Name of the project (used for container naming)"
  type        = string
  default     = "fortress"
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  sensitive   = true  # Ne sera pas affiché dans les logs
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "warehouse"
}

variable "postgres_port" {
  description = "PostgreSQL external port"
  type        = number
  default     = 5433
}

variable "minio_root_user" {
  description = "MinIO root username"
  type        = string
  sensitive   = true
}

variable "minio_root_password" {
  description = "MinIO root password"
  type        = string
  sensitive   = true
}

variable "minio_api_port" {
  description = "MinIO API port"
  type        = number
  default     = 9000
}

variable "minio_console_port" {
  description = "MinIO web console port"
  type        = number
  default     = 9001
}
