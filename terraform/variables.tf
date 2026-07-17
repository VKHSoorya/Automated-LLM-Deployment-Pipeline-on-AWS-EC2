variable "instance_type" {
  description = "The type of instance to use"
  type        = string
  default     = "t3.micro"
  
}

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-south-1"
}

variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance"
  type        = string
  default     = "ami-01a00762f46d584a1"
}

variable "key_name" {
  description = "The name of the key pair to use for the EC2 instance"
  type        = string
  default     = "keypair1"
}

variable "subnet_id" {
  description = "The ID of the subnet to launch the EC2 instance in"
  type        = string
  default     = "subnet-0675df46f50e65c62"
}

variable "ssh_user" {
  default = "ubuntu"
}

variable "private_key_path" {
  type = string
}

variable "model_name" {
  description = "Model to deploy"
  type        = string
  default     = "llama3.2"
}