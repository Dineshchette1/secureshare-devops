variable "region" {
  description = "AWS region. The account's SCP restricts this to us-east-2."
  type        = string
  default     = "us-east-2"
}

variable "environment" {
  description = "Environment name, used in tags and resource names."
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name, used as a prefix for resource names."
  type        = string
  default     = "secureshare"
}

variable "vpc_cidr" {
  description = "IP range for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "az_count" {
  description = "How many availability zones to spread subnets across."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "Use 2 or 3 AZs: the load balancer requires at least 2."
  }
}

variable "app_port" {
  description = "Port the application container listens on."
  type        = number
  default     = 8000
}
