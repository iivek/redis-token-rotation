variable "MYSQL_ROOT_PASSWORD" {}
variable "MYSQL_DATABASE" {}
variable "MYSQL_USER" {}
variable "MYSQL_PASSWORD" {}
variable "REDIS_PASSWORD" {}


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
