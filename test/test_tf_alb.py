import unittest
from string import ascii_letters, digits
from subprocess import check_call, check_output

from hypothesis import example, given
from hypothesis.strategies import text


def filter_invalid_hyphens(name):
    return (
        len(name.replace('-', '')) > 0
        and not name.startswith('-')
        and not name.endswith('-')
    )


class TestTFALB(unittest.TestCase):

    def setUp(self):
        check_call(['terraform', 'get', 'test/infra'])

    @given(text(
        alphabet=ascii_letters+digits+'-', min_size=10, average_size=34,
    ).filter(filter_invalid_hyphens))
    @example('a'*31 + '-' + 'b'*10)
    def test_create_alb(self, name):
        # Given
        subnet_ids = (
            "[\"subnet-b46032ec\", \"subnet-ca4311ef\", \"subnet-ba881221\"]"
        )

        # When
        output = check_output([
            'terraform',
            'plan',
            '-var', 'name={}'.format(name),
            '-var', 'vpc_id=foobar',
            '-var', 'subnet_ids={}'.format(subnet_ids),
            '-var', 'default_target_group_arn=foobar',
            '-target=module.alb_test',
            '-no-color',
            'test/infra'
        ]).decode('utf-8')

        # Then
        assert """
+ module.alb_test.aws_alb.alb
    access_logs.#:              "1"
    access_logs.0.enabled:      "false"
    access_logs.0.prefix:       "{name}"
    arn:                        "<computed>"
    arn_suffix:                 "<computed>"
    dns_name:                   "<computed>"
    enable_deletion_protection: "false"
    idle_timeout:               "60"
    internal:                   "true"
    ip_address_type:            "<computed>"
    name:                       "{compact_name}"
    security_groups.#:          "<computed>"
    subnets.#:                  "3"
    subnets.2009589885:         "subnet-ca4311ef"
    subnets.3117197332:         "subnet-ba881221"
    subnets.416118645:          "subnet-b46032ec"
    vpc_id:                     "<computed>"
    zone_id:                    "<computed>"
        """.format(
                compact_name=name[:32].strip('-'),
                name=name
            ).strip() in output

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
        assert """
+ module.alb_test_with_tags.aws_alb.alb
    access_logs.#:              "1"
    access_logs.0.enabled:      "false"
    access_logs.0.prefix:       "albalbalb"
    arn:                        "<computed>"
    arn_suffix:                 "<computed>"
    dns_name:                   "<computed>"
    enable_deletion_protection: "false"
    idle_timeout:               "60"
    internal:                   "true"
    ip_address_type:            "<computed>"
    name:                       "albalbalb"
    security_groups.#:          "<computed>"
    subnets.#:                  "3"
        """.strip() in output

        assert """
    tags.%:                     "2"
    tags.component:             "component"
    tags.service:               "service"
    vpc_id:                     "<computed>"
    zone_id:                    "<computed>"
        """.strip() in output

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
        assert """
+ module.alb_test.aws_alb_listener.https
    arn:                               "<computed>"
    certificate_arn:                   "${module.aws_acm_certificate_arn.arn}"
    default_action.#:                  "1"
    default_action.0.target_group_arn: "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-targets/73e2d6bc24d8a067"
    default_action.0.type:             "forward"
    load_balancer_arn:                 "${aws_alb.alb.arn}"
    port:                              "443"
    protocol:                          "HTTPS"
    ssl_policy:                        "<computed>"
        """.strip() in output # noqa

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
        assert """
+ module.alb_test.aws_security_group.default
    description:                           "Managed by Terraform"
    egress.#:                              "1"
    egress.482069346.cidr_blocks.#:        "1"
    egress.482069346.cidr_blocks.0:        "0.0.0.0/0"
    egress.482069346.from_port:            "0"
    egress.482069346.ipv6_cidr_blocks.#:   "0"
    egress.482069346.prefix_list_ids.#:    "0"
    egress.482069346.protocol:             "-1"
    egress.482069346.security_groups.#:    "0"
    egress.482069346.self:                 "false"
    egress.482069346.to_port:              "0"
    ingress.#:                             "1"
    ingress.2617001939.cidr_blocks.#:      "1"
    ingress.2617001939.cidr_blocks.0:      "0.0.0.0/0"
    ingress.2617001939.from_port:          "443"
    ingress.2617001939.ipv6_cidr_blocks.#: "0"
    ingress.2617001939.protocol:           "tcp"
    ingress.2617001939.security_groups.#:  "0"
    ingress.2617001939.self:               "false"
    ingress.2617001939.to_port:            "443"
    name:                                  "<computed>"
    owner_id:                              "<computed>"
    vpc_id:                                "vpc-2f09a348"
        """.strip() in output
