output "arn" {
  value = "${element(concat(data.aws_acm_certificate.cert.*.arn, list("")), 0)}"
}