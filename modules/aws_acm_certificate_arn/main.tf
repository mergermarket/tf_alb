data "aws_acm_certificate" "cert" {
  domain   = "${var.domain_name}"
  statuses = ["ISSUED"]
}

variable "domain_name" {
  description = ""
  type        = "string"
}

output "arn" {
  value = "${data.aws_acm_certificate.cert.arn}"
}
