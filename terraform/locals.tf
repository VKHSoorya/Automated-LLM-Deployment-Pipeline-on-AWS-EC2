data "http" "my_ip" {
  url = "https://checkip.amazonaws.com/"
}

locals {
  laptop_ip = "${chomp(data.http.my_ip.response_body)}/32"
}