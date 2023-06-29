terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

resource "docker_container" "redis" {
  image = "redis:latest"
  name  = "local-redis"
  ports {
    internal = 6379
    external = 6379
  }
}
