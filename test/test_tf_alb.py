import re
import unittest

from string import ascii_letters, digits
from subprocess import check_call, check_output


def filter_invalid_hyphens(name):
    return (
        len(name.replace('-', '')) > 0
        and not name.startswith('-')
        and not name.endswith('-')
    )


def template_to_re(t):
    seen = dict()

    def pattern(placeholder, open_curly, close_curly, text, whitespace):
        if text is not None:
            return re.escape(text)
        elif whitespace is not None:
            return r'\s+'
        elif open_curly is not None:
            return r'\{'
        elif close_curly is not None:
            return r'\}'
        elif seen.get(placeholder):
            return '(?P={})'.format(placeholder)
        else:
            seen[placeholder] = True
            return '(?P<{}>.*?)'.format(placeholder)

    return "".join([
        pattern(*match.groups())
        for match in re.finditer(
            r'{([\w_]+)}|(\{\{)|(\}\})|([^{}\s]+)|(\s+)', t
        )
    ])


class TestTFALB(unittest.TestCase):

    def setUp(self):
        check_call(['terraform', 'init', 'test/infra'])
        check_call(['terraform', 'get', 'test/infra'])

    def test_create_alb(self):
        # Given
        subnet_ids = (
            "[\"subnet-b46032ec\", \"subnet-ca4311ef\", \"subnet-ba881221\"]"
        )

        # When
        output = check_output([
            'terraform',
            'plan',
            '-var', 'name=super-nice-alb-name',
            '-var', 'vpc_id=foobar',
            '-var', 'subnet_ids={}'.format(subnet_ids),
            '-var', 'default_target_group_arn=foobar',
            '-target=module.alb_test',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')

        # Then
        assert re.search(template_to_re("""
      access_logs.#:                         "1"
      access_logs.0.enabled:                 "false"
      arn:                                   <computed>
      arn_suffix:                            <computed>
      dns_name:                              <computed>
      enable_deletion_protection:            "false"
      enable_http2:                          "true"
      idle_timeout:                          "60"
      internal:                              "true"
      ip_address_type:                       <computed>
      load_balancer_type:                    "application"
      name:                                  "super-nice-alb-name"
      security_groups.#:                     <computed>
      subnet_mapping.#:                      <computed>
      subnets.#:                             "3"
      subnets.2009589885:                    "subnet-ca4311ef"
      subnets.3117197332:                    "subnet-ba881221"
      subnets.416118645:                     "subnet-b46032ec"
      vpc_id:                                <computed>
      zone_id:                               <computed>
        """.strip()), output)

    def test_create_alb_with_tags(self):
        # Given
        subnet_ids = (
            "[\"subnet-b46032ec\", \"subnet-ca4311ef\", \"subnet-ba881221\"]"
        )

        # When
        output = check_output([
            'terraform',
            'plan',
            '-var', 'name=albalbalb',
            '-var', 'vpc_id=foobar',
            '-var', 'subnet_ids={}'.format(subnet_ids),
            '-var', 'default_target_group_arn=foobar',
            '-target=module.alb_test_with_tags',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')

        # Then
        assert re.search(template_to_re("""
      access_logs.#:                         "1"
      access_logs.0.enabled:                 "false"
      arn:                                   <computed>
      arn_suffix:                            <computed>
      dns_name:                              <computed>
      enable_deletion_protection:            "false"
      enable_http2:                          "true"
      idle_timeout:                          "60"
      internal:                              "true"
      ip_address_type:                       <computed>
      load_balancer_type:                    "application"
      name:                                  "albalbalb"
      security_groups.#:                     <computed>
      subnet_mapping.#:                      <computed>
      subnets.#:                             "3"
      subnets.2009589885:                    "subnet-ca4311ef"
      subnets.3117197332:                    "subnet-ba881221"
      subnets.416118645:                     "subnet-b46032ec"
      tags.%:                                "2"
      tags.component:                        "component"
      tags.service:                          "service"
      vpc_id:                                <computed>
      zone_id:                               <computed>
        """.strip()), output)

    def test_create_listener(self):
        # Given
        default_target_group_arn = (
            "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/"
            "my-targets/73e2d6bc24d8a067"
        )

        # When
        output = check_output([
            'terraform',
            'plan',
            '-var', 'name=foobar',
            '-var', 'vpc_id=foobar',
            '-var', 'subnet_ids=["foo", "bar", "foo"]',
            '-var', 'certificate_domain_name=foobar.com',
            '-var', 'default_target_group_arn={}'.format(
                default_target_group_arn
            ),
            '-target=module.alb_test',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')

        # Then
        assert re.search(template_to_re("""
      default_action.#:                      "1"
      default_action.0.order:                <computed>
      default_action.0.target_group_arn:     "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/73e2d6bc24d8a067"
      default_action.0.type:                 "forward"
        """.strip()), output)  # noqa

        assert re.search(template_to_re("""
      port:                                  "443"
      protocol:                              "HTTPS"
      ssl_policy:                            <computed>
        """.strip()), output)

    def test_create_security_group(self):
        # Given
        vpc_id = "vpc-2f09a348"

        # When
        output = check_output([
            'terraform',
            'plan',
            '-var', 'name=foo',
            '-var', 'vpc_id={}'.format(vpc_id),
            '-var', 'subnet_ids=["foo", "bar", "foo"]',
            '-var', 'certificate_domain_name=foobar.com',
            '-var', 'default_target_group_arn=foobar',
            '-target=module.alb_test',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')

        # Then
        assert re.search(template_to_re("""
      egress.#:                              "1"
      egress.{ident}.cidr_blocks.#:        "1"
      egress.{ident}.cidr_blocks.0:        "0.0.0.0/0"
      egress.{ident}.description:          ""
      egress.{ident}.from_port:            "0"
      egress.{ident}.ipv6_cidr_blocks.#:   "0"
      egress.{ident}.prefix_list_ids.#:    "0"
      egress.{ident}.protocol:             "-1"
      egress.{ident}.security_groups.#:    "0"
      egress.{ident}.self:                 "false"
      egress.{ident}.to_port:              "0"
        """.strip()), output)

        assert re.search(template_to_re("""
      ingress.#:                             "2"
      ingress.{ident}.cidr_blocks.#:      "1"
      ingress.{ident}.cidr_blocks.0:      "0.0.0.0/0"
      ingress.{ident}.description:        ""
      ingress.{ident}.from_port:          "80"
      ingress.{ident}.ipv6_cidr_blocks.#: "0"
      ingress.{ident}.prefix_list_ids.#:  "0"
      ingress.{ident}.protocol:           "tcp"
      ingress.{ident}.security_groups.#:  "0"
      ingress.{ident}.self:               "false"
      ingress.{ident}.to_port:            "80"
        """.strip()), output)

        assert re.search(template_to_re("""
      ingress.{ident}.cidr_blocks.#:      "1"
      ingress.{ident}.cidr_blocks.0:      "0.0.0.0/0"
      ingress.{ident}.description:        ""
      ingress.{ident}.from_port:          "443"
      ingress.{ident}.ipv6_cidr_blocks.#: "0"
      ingress.{ident}.prefix_list_ids.#:  "0"
      ingress.{ident}.protocol:           "tcp"
      ingress.{ident}.security_groups.#:  "0"
      ingress.{ident}.self:               "false"
      ingress.{ident}.to_port:            "443"
        """.strip()), output)

        assert re.search(template_to_re("""
      revoke_rules_on_delete:                "false"
      vpc_id:                                "vpc-2f09a348"
        """.strip()), output)
