provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "secureshare"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
