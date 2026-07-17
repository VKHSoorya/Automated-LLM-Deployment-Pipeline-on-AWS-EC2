provider "aws" {
  region = var.aws_region
}

# terraform {
#   required_providers {
#     aws = {
#       source = "hashicorp/aws"
#     }

#     http = {
#       source = "hashicorp/http"
#     }

#     local = {
#       source = "hashicorp/local"
#     }

#     null = {
#       source = "hashicorp/null"
#     }

#     time = {
#       source = "hashicorp/time"
#     }
    
#   }
# }
