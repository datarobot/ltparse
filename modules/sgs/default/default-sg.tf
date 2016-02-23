variable "run_id" {}
variable "label" {
    default = "enterprise"
}
variable "vpc_id" {}

output "id" {
    value = "${aws_security_group.default_security_group.id}"
}

resource "aws_security_group" "default_security_group" {
  name = "${var.label}_${var.run_id}"
  description = "Default enterprise security group for test ${var.run_id}"
  vpc_id = "${var.vpc_id}"

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "38.88.168.107/32",
      "10.16.0.0/16",
      "10.9.0.0/16",
      "10.20.0.0/16"
    ]
    self = true
  }
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = [
      "38.88.168.107/32",
      "10.16.0.0/16",
      "10.9.0.0/16",
      "10.20.0.0/16"
    ]
    self = true
  }
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [
      "38.88.168.107/32",
      "10.16.0.0/16",
      "10.9.0.0/16",
      "10.20.0.0/16"
    ]
    self = true
  }
  ingress {
    from_port = "-1"
    to_port = "-1"
    protocol = "icmp"
    cidr_blocks = [
      "38.88.168.107/32",
      "10.16.0.0/16",
      "10.9.0.0/16",
      "10.20.0.0/16"
    ]
    self = true
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags {
    Name = "${var.label}"
  }
}
