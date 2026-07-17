output "ec2_public_ip" {
  value = module.ec2_instance.public_ip
}

output "instance_id" {
  value = module.ec2_instance.id
}