# /*
#   Pignus-Api
#   Load Balancer

# */

# resource "aws_security_group" "alb" {
#   name        = "terraform_alb_security_group"
#   description = "Terraform load balancer security group"
#   vpc_id      = "${aws_vpc.vpc.id}"

#   ingress {
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = "${var.allowed_cidr_blocks}"
#   }

#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = "${var.allowed_cidr_blocks}"
#   }

#   # Allow all outbound traffic.
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags {
#     Name = "terraform-example-alb-security-group"
#   }
# }

resource "aws_lb" "pignus" {
  name               = "Pignus"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pignus_lb_ingress.id]
  subnets            = [aws_subnet.pignus_public_a.id, aws_subnet.pignus_private_b.id]

  enable_deletion_protection = false

  # access_logs {
  #   bucket  = aws_s3_bucket.lb_logs.bucket
  #   prefix  = "test-lb"
  #   enabled = true
  # }

  tags = {
    app = "pignus"
  }
}

resource "aws_lb_target_group" "pignus_gateway" {
  name     = "Pignus-Gateway"
  protocol = "HTTPS"
  vpc_id   = aws_vpc.pignus.id
  target_type = "lambda"
}