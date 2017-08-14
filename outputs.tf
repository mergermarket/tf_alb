output "alb_dns_name" {
  value = "${aws_alb.alb.dns_name}"
}

output "alb_listener_arn" {
  value = "${aws_alb_listener.https.arn}"
}

output "alb_arn" {
  value = "${aws_alb.alb.arn}"
}
