# terraform/monitoring.tf

# Prometheus
resource "docker_container" "prometheus" {
  name  = "fortress-prometheus"
  image = docker_image.prometheus.image_id
  user  = "nobody"

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
    "--storage.tsdb.path=/prometheus"
  ]

  networks_advanced {
    name = docker_network.fortress_network.name
    aliases = ["prometheus"]  # Important: DNS alias
  }

  restart = "unless-stopped"
}

resource "docker_image" "prometheus" {
  name = "prom/prometheus:latest"
}

# Grafana
resource "docker_container" "grafana" {
  name  = "fortress-grafana"
  image = docker_image.grafana.image_id

  ports {
    internal = 3000
    external = 3001
  }

  env = [
    "GF_SECURITY_ADMIN_USER=admin",
    "GF_SECURITY_ADMIN_PASSWORD=fortress2024",
    "GF_INSTALL_PLUGINS=",
    "GF_SERVER_ROOT_URL=http://localhost:3001"
  ]

  volumes {
    host_path      = "${path.cwd}/../data/grafana"
    container_path = "/var/lib/grafana"
  }

  volumes {
    host_path      = "${path.cwd}/../monitoring/grafana/provisioning"
    container_path = "/etc/grafana/provisioning"
  }

  networks_advanced {
    name = docker_network.fortress_network.name
    aliases = ["grafana"]  # Important: DNS alias
  }

  restart = "unless-stopped"
  
  depends_on = [docker_container.prometheus]
}

resource "docker_image" "grafana" {
  name = "grafana/grafana:latest"
}

# Outputs
output "prometheus_url" {
  value       = "http://localhost:9090"
  description = "Prometheus UI URL"
}

output "grafana_url" {
  value       = "http://localhost:3001"
  description = "Grafana UI URL (admin/fortress2024)"
}
