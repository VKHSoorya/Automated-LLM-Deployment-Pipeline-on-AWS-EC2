module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "single-instance"
  ami = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name
  subnet_id     = var.subnet_id
  associate_public_ip_address = true

  security_group_ingress_rules = {
    ssh = {
      description = "Allow SSH access"
      from_port   = 22
      to_port     = 22
      ip_protocol    = "tcp"
      cidr_ipv4 = local.laptop_ip
      # cidr_blocks    = ["0.0.0.0/0"]
    }

    ollamaport = {
      description = "Allow HTTP access"
      from_port   = 11434
      to_port     = 11434
      ip_protocol    = "tcp"
      cidr_ipv4 = local.laptop_ip
      }
  }

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }


}

# resource "time_sleep" "wait_for_ssh" {
#   depends_on = [module.ec2_instance]

#   create_duration = "60s"
# }

output "instance_details" {
  value={
    
    id = module.ec2_instance.id
    public_ip = module.ec2_instance.public_ip

  }
} 