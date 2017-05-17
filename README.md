AWS ALB terraform module
======================================

This module creates AWS Application Load Balancer as per provided parameters.

As some more resources - security-group and listener are required when creating AWS ALB, these are also created (based on passed parameters).

This module will output AWS ALB's `dns_name` and `listener_arn` which can be used to integrate with it.

Module Input Variables
----------------------
- `name` - (string) - **REQUIRED** - The name of the ALB. This name must be unique within your AWS account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen
- `vpc_id` - (string) - **REQUIRED** - The id of the VPC that the ALB should be placed in
- `subnet_ids` - (list) - **REQUIRED** - A list of subnet IDs to attach to the ALB
- `certificate_arn` - (string) - **REQUIRED** - The ARN of the SSL server certificate. Exactly one certificate is required if the protocol is HTTPS
- `default_target_group_arn` - (string) - **REQUIRED** - The ARN of the default Target Group to which to route traffic
- `internal` - (bool) - OPTIONAL - If true, the ALB will be internal; default: `true`
- `extra_security_groups` - list - OPTIONAL - Extra security groups to be attached to ALB

Usage
-----
```hcl
module "alb_test" {
  source = "github.com/mergermarket/tf_alb"

  # required
  name                     = "foobar-alb"
  vpc_id                   = "vpc-2f09a348"
  subnet_ids               = ["subnet-b46032ec", "subnet-ca4311ef", "subnet-ba881221"]
  certificate_arn          = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
  default_target_group_arn = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/73e2d6bc24d8a067"
}
```

Outputs
-------
- `alb_dns_name` - The DNS name of the load balancer
- `alb_listener_arn` - The ARN of the load balancer
