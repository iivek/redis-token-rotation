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
  env = [
    # "REDIS_PASSWORD=${var.REDIS_PASSWORD}"
  ]
}

resource "docker_container" "mysql" {
  image = "mysql:latest"
  name  = "local-mysql"
  env   = [
    "MYSQL_ROOT_PASSWORD=${var.MYSQL_ROOT_PASSWORD}",
    "MYSQL_DATABASE=${var.MYSQL_DATABASE}",
    "MYSQL_USER=${var.MYSQL_USER}",
    "MYSQL_PASSWORD=${var.MYSQL_PASSWORD}",
  ]
  ports {
    internal = 3306
    external = 3306
  }
}
