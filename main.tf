module "aws_acm_certificate_arn" {
  source      = "./modules/aws_acm_certificate_arn"
  run_data    = "${var.run_data}"
  domain_name = "${var.certificate_domain_name}"
}

resource "aws_alb" "alb" {
  name            = "${replace(replace(var.name, "/(.{0,32}).*/", "$1"), "/^-+|-+$/", "")}"
  internal        = "${var.internal}"
  security_groups = ["${concat(list(aws_security_group.default.id), var.extra_security_groups)}"]
  subnets         = "${var.subnet_ids}"
  tags            = "${var.tags}"
  idle_timeout    = "${var.idle_timeout}"

  access_logs {
    bucket  = "${var.access_logs_bucket}"
    enabled = "${var.access_logs_enabled}"
  }
}

resource "aws_alb_listener" "https" {
  load_balancer_arn = "${aws_alb.alb.arn}"
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = "${module.aws_acm_certificate_arn.arn}"

  default_action {
    target_group_arn = "${var.default_target_group_arn}"
    type             = "forward"
  }
}
