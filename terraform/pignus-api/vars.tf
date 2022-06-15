/*
  Pignus-Api
  Variables

*/

variable "aws_account" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "pignus_image" {
  type = string
}

variable "pignus_database_name" {
  type = string
}

variable "pignus_cidr_block" {
  type = string
}

variable "pignus_cidr_subnet_a_public" {
  type = string
}

variable "pignus_cidr_subnet_b_public" {
  type = string
}

variable "pignus_cidr_subnet_b_private" {
  type = string
}

variable "pignus_debug" {
  type = string
  default = "false"
}

# Whether or not to connect the RDS instance to netskope
variable "netskope_conx" {
  type = string
}

# Netskope accepted CIDR ranger
variable "netskope_cidr" {
  type = string
}

# Netskope/Pignus VPC peering connection
variable "netskope_pcx" {
  type = string
}

# End File: automox/pignus/terraform/pignus-api/vars.tf
