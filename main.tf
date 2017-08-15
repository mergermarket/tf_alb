resource "aws_alb" "alb" {
  name            = "${replace(replace(var.name, "/(.{0,32}).*/", "$1"), "/^-+|-+$/", "")}"
  internal        = "${var.internal}"
  security_groups = ["${concat(list(aws_security_group.default.id), var.extra_security_groups)}"]
  subnets         = "${var.subnet_ids}"
}

resource "aws_alb_listener" "https" {
  load_balancer_arn = "${aws_alb.alb.arn}"
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = "${var.certificate_arn}"

  default_action {
    target_group_arn = "${var.default_target_group_arn}"
    type             = "forward"
  }
}
