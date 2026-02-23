# terraform/monitoring.tf
# Monitoring infrastructure with Prometheus

# Prometheus container
resource "docker_container" "prometheus" {
  name  = "fortress-prometheus"
  image = docker_image.prometheus.image_id

  ports {
    internal = 9090
    external = 9090
  }

  volumes {
    host_path      = "${path.cwd}/../monitoring/prometheus"
    container_path = "/etc/prometheus"
  }

  volumes {
    host_path      = "${path.cwd}/../data/prometheus"
    container_path = "/prometheus"
  }

  command = [
    "--config.file=/etc/prometheus/prometheus.yml",
    "--storage.tsdb.path=/prometheus",
    "--web.console.libraries=/etc/prometheus/console_libraries",
    "--web.console.templates=/etc/prometheus/consoles"
  ]

  networks_advanced {
    name = docker_network.fortress_network.name
  }

  restart = "unless-stopped"
}

resource "docker_image" "prometheus" {
  name = "prom/prometheus:latest"
}

# Dagster metrics exporter
resource "docker_container" "dagster_exporter" {
  name  = "fortress-dagster-exporter"
  image = docker_image.dagster_exporter.image_id

  ports {
    internal = 8000
    external = 8000
  }

  networks_advanced {
    name = docker_network.fortress_network.name
  }

  restart = "unless-stopped"
}

resource "docker_image" "dagster_exporter" {
  name = "fortress-dagster-exporter:latest"
  build {
    context    = "${path.cwd}/../monitoring/exporters"
    dockerfile = "Dockerfile"
  }
}

# Outputs
output "prometheus_url" {
  value       = "http://localhost:9090"
  description = "Prometheus UI URL"
}

output "dagster_exporter_metrics_url" {
  value       = "http://localhost:8000/metrics"
  description = "Dagster metrics endpoint"
}
