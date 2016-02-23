DEFAULT_INSTANCE = {
        'ami': '${var.ami_ids.hvm}',
        'associate_public_ip_address': True,
        'availability_zone': 'us-east-1a',
        'count': 1,
        'instance_type': 'm3.large',
        'key_name': '${var.aws.key_name}',
        'subnet_id': '${terraform_remote_state.subnets.output.us-east-1a}',
        'tags': {
            'label': 'worker',
            'owner': 'test_${var.run_id}',
            'user': '${var.build_user}',
            'name': 'enterprise_test'
            },
        'vpc_security_group_ids': ['${module.default_security_group.id}']
        }

DEFAULT_SECURITY_GROUP = {
        'label': 'default_security_group',
        'source': 'modules/sgs/default'
        }

DEFAULT_ELB = {
        'subnets': [
            "${terraform_remote_state.subnets.output.us-east-1a}",
            "${terraform_remote_state.subnets.output.us-east-1b}",
            "${terraform_remote_state.subnets.output.us-east-1d}"
            ],
        'instances': [
            "${aws_instance.papi1.id}",
            "${aws_instance.papi2.id}",
            "${aws_instance.papi3.id}"
            ],
        'internal': True,
        'health_check': {
            'healthy_threshold': 10,
            'interval': 5,
            'unhealthy_threshold': 2,
            'target': 'HTTP:80/ping',
            'timeout': 4
            },
        'listener': {
            'instance_port': 80,
            'instance_protocol': 'http',
            'lb_port': 80,
            'lb_protocol': 'http'
            },
        'tags': {
            'Name': 'enterprise-test-${var.run_id}'
            }
        }

DEFAULT_ROUTE53_RECORD = {
        'zone_id': '${var.aws.zone_id}',
        'name': '${var.run_id}.${var.domain}',
        'type': 'A',
        'ttl': 300,
        'records': ["${aws_instance.webserver.private_ip}"]
        }
