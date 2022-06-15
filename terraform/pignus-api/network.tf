/*
  Pignus-Api
  Network
    VPC: Pignus
    Internet Gateway: Pignus
    Elastic IP: Pignus
    NAT Gateway: Pignus
    Subnets: Pignus-A, Pignus-B
    Route Tables: Pignus-Public, Pignus-Private
    Route Table Associations: Pignus-Public <> Pignus-A, Pignus-Private <> Pignus-B
    Network Interface
    Subnet Group: pignus
    Security Group: Pignus-RDS, Pignus-Lambda-to-RDS, Pignus-Egress-All

*/

# VPC: Pignus
resource "aws_vpc" "pignus" {
  cidr_block = var.pignus_cidr_block
  tags = {
    Name      = "Pignus"
    team      = "secops"
    terraform = "true"
    flowlog   = "all"
    app       = "pignus"
  }
}

# Internet Gateway: Pignus
resource "aws_internet_gateway" "pignus" {
  vpc_id = aws_vpc.pignus.id

  tags = {
    Name      = "Pignus"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }

}

# Elastic IP: Pignus
resource "aws_eip" "pignus" {
  vpc = true
  tags = {
    Name      = "Pignus"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}


# NAT Gateway: Pignus
resource "aws_nat_gateway" "pignus" {
  allocation_id = aws_eip.pignus.id
  subnet_id     = aws_subnet.pignus_public_a.id

  tags = {
    Name      = "Pignus"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }

  depends_on = [aws_internet_gateway.pignus, aws_eip.pignus, aws_subnet.pignus_public_a]
}


# Create public network resources
# Subnet: Pignus-A-Public
resource "aws_subnet" "pignus_public_a" {
  vpc_id            = aws_vpc.pignus.id
  cidr_block        = var.pignus_cidr_subnet_a_public
  availability_zone = "${var.aws_region}a"
  tags = {
    Name      = "Pignus-Public-A"
    team      = "secops"
    terraform = "true"
  }
}
# Route Table: Pignus-Public
resource "aws_route_table" "pignus_public" {
  vpc_id = aws_vpc.pignus.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.pignus.id
  }
  # route {
  #   cidr_block                = var.netskope_cidr
  #   vpc_peering_connection_id = var.netskope_pcx
  # }

  tags = {
    Name      = "Pignus-Public-A"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}
# Route Table Association: Pignus-Public <> Pignus-A
resource "aws_route_table_association" "pignus_public" {
  subnet_id      = aws_subnet.pignus_public_a.id
  route_table_id = aws_route_table.pignus_public.id

  depends_on = [aws_route_table.pignus_public]
}

# Create second availablilty zone public network resources
# Subnet: Pignus-Public-B
resource "aws_subnet" "pignus_public_b" {
  vpc_id            = aws_vpc.pignus.id
  cidr_block        = var.pignus_cidr_subnet_b_public
  availability_zone = "${var.aws_region}b"
  tags = {
    Name      = "Pignus-Public-B"
    team      = "secops"
    terraform = "true"
  }
}
# Route Table: Pignus-B-Public 
resource "aws_route_table" "pignus_public_b" {
  vpc_id = aws_vpc.pignus.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.pignus.id
  }
  # route {
  #   cidr_block                = var.netskope_cidr
  #   vpc_peering_connection_id = var.netskope_pcx
  # }
  tags = {
    Name      = "Pignus-Public-B"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}
# Route Table Association: Pignus-Public-B <> Pignus-B
resource "aws_route_table_association" "pignus_public_b" {
  subnet_id      = aws_subnet.pignus_public_b.id
  route_table_id = aws_route_table.pignus_public_b.id
  depends_on = [aws_route_table.pignus_public_b]
}


# Create private resources
# Subnet: Pignus-B
resource "aws_subnet" "pignus_private_b" {
  vpc_id            = aws_vpc.pignus.id
  cidr_block        = var.pignus_cidr_subnet_b_private
  availability_zone = "${var.aws_region}b"

  tags = {
    Name      = "Pignus-Private-B"
    team      = "secops"
    terraform = "true"
  }
}
# Route Table: Pignus-Private
resource "aws_route_table" "pignus_private_b" {
  vpc_id = aws_vpc.pignus.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.pignus.id
  }
  # route {
  #   cidr_block                = var.netskope_cidr
  #   vpc_peering_connection_id = var.netskope_pcx
  # }
  depends_on = [aws_nat_gateway.pignus]
  tags = {
    Name      = "Pignus-Private-B"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}
# Route Table Assoctiation: Pignus-Private - Pignus-B
resource "aws_route_table_association" "pignus_private_b" {
  subnet_id      = aws_subnet.pignus_private_b.id
  route_table_id = aws_route_table.pignus_private_b.id
  depends_on = [aws_route_table.pignus_private_b]
}
# Route Table Association: Pignus-Private <> Pignus-B
resource "aws_network_interface" "pignus" {
  description     = "Pignus network interface for NAT Gateway"
  subnet_id       = aws_subnet.pignus_private_b.id
  private_ips     = ["10.32.6.10"]
  security_groups = [aws_security_group.pignus_egress_all.id]
  tags = {
    Name      = "Pignus"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}


# Subnet Group
resource "aws_db_subnet_group" "pignus" {
  name       = "pignus"
  subnet_ids = [
    aws_subnet.pignus_public_a.id,
    aws_subnet.pignus_public_b.id, 
    aws_subnet.pignus_private_b.id
  ]

  depends_on = [aws_route_table.pignus_public, aws_route_table.pignus_public_b]
  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# Security Groups
# Security Group: Pignus-RDS
#
resource "aws_security_group" "pignus_rds_ingress" {
  name   = "Pignus-RDS-Ingress"
  vpc_id = aws_vpc.pignus.id

  ingress = [
    {
      cidr_blocks      = [
      var.pignus_cidr_subnet_a_public,
      var.pignus_cidr_subnet_b_public,
      var.pignus_cidr_subnet_b_private
      ]
      description      = ""
      from_port        = 3306
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 3306
    }
  ]

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# Security Group: Pignus-Lambda-to-RDS
resource "aws_security_group" "pignus_lambda_rds" {
  name   = "Pignus-Lambda-RDS"
  vpc_id = aws_vpc.pignus.id

  egress {
    from_port   = 3600
    to_port     = 3600
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# Security Group: Pignus-Egress-All
resource "aws_security_group" "pignus_egress_all" {
  name   = "Pignus-Egress-All"
  vpc_id = aws_vpc.pignus.id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name      = "Pignus-Egress-All"
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# Security Group: Pignus-Netskope
# resource "aws_security_group" "pignus_netskope" {
#   name   = "Pignus-Netskope"
#   vpc_id = aws_vpc.pignus.id

#   ingress = [
#     {
#       cidr_blocks      = [var.netskope_cidr]
#       description      = ""
#       from_port        = 3306
#       ipv6_cidr_blocks = []
#       prefix_list_ids  = []
#       protocol         = "tcp"
#       security_groups  = []
#       self             = false
#       to_port          = 3306
#     }
#   ]
#   tags = {
#     team      = "secops"
#     terraform = "true"
#     app       = "pignus"
#   }
# }

resource "aws_security_group" "pignus_lb_ingress" {
  name   = "Pignus-LB-Ingress"
  vpc_id = aws_vpc.pignus.id

  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 80
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 80
    },
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 443
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 443
    }
  ]

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

resource "aws_security_group" "pignus_efs" {
  name   = "Pignus-EFS"
  vpc_id = aws_vpc.pignus.id

  ingress = [
    {
      cidr_blocks      = [var.pignus_cidr_block]
      description      = "Ingress for Pignus EFS"
      from_port        = 2049
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 2049
    }
  ]
  egress = [
    {
      cidr_blocks      = [var.pignus_cidr_block]
      description      = "Egress for Pignus EFS"
      from_port        = 2049
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 2049
    }
  ]

  tags = {
    team      = "secops"
    terraform = "true"
    app       = "pignus"
  }
}

# End File: automox/pignus/terraform/pignus-api/network.tf
