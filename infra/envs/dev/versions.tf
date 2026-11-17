terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # State lives in the bucket created by infra/bootstrap.
  # use_lockfile uses S3's native locking (Terraform 1.10+), so no
  # DynamoDB table is needed.
  backend "s3" {
    bucket       = "secureshare-tfstate-868701002330"
    key          = "envs/dev/terraform.tfstate"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }
}
