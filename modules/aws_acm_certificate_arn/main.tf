data "aws_acm_certificate" "cert" {
  count    = "${var.run_data}"
  domain   = "${var.domain_name}"
  statuses = ["ISSUED"]
}
