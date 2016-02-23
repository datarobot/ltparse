variable "run_id" {}
variable "label" {
    default = "enterprise_public"
}
variable "vpc_id" {}

output "id" {
    value = "${aws_security_group.default_security_group.id}"
}

resource "aws_security_group" "default_security_group" {
  name = "${var.label}_${var.run_id}_public"
  description = "Public-facing enterprise security group for test ${var.run_id}"
  vpc_id = "${var.vpc_id}"

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    self = true
  }
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
    self = true
  }
  tags {
    Name = "${var.label}"
  }
}
