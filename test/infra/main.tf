# fixture
module "alb_test" {
  source = "../.."

  # required
  name                     = "${var.name}"
  vpc_id                   = "${var.vpc_id}"
  subnet_ids               = "${var.subnet_ids}"
  certificate_arn          = "${var.certificate_arn}"
  default_target_group_arn = "${var.default_target_group_arn}"
}

# configure provider to not try too hard talking to AWS API
provider "aws" {
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_get_ec2_platforms      = true
  skip_region_validation      = true
  skip_requesting_account_id  = true
  max_retries                 = 1
  access_key                  = "a"
  secret_key                  = "a"
  region                      = "eu-west-1"
}

# variables
variable "name" {}

variable "vpc_id" {}

variable "subnet_ids" {
  type = "list"
}

variable "certificate_arn" {}

variable "default_target_group_arn" {}
