"""
Trafaret-based schema for layout validation.
(see http://trafaret.readthedocs.org/en/latest/intro.html)

LAYOUT.check(data) is called during the cli and all layouts in
tests/layouts/good/*.yaml are tested with this schema.
"""
import trafaret as t
import yaml


GENERIC_DICT = t.Dict().allow_extra('*')


# Valid UNIX absolute file path. `/` followed by one or more non-null chars
ABSOLUTE_PATH = t.String(regex=r'/[^/\0]([^\0]+)?')


# Valid EC2 instance type (eg. m3.2xlarge)
INSTANCE_TYPE = t.String(
        regex=r'[tmcgrid][234]\.(nano|micro|small|medium|([2468]|10)?x?large)')


EBS_VOLUME = t.Dict({
    t.Key('volume_size'): t.Int(gt=0, lt=5000),
    t.Key('mountpoint', optional=True): ABSOLUTE_PATH,
    t.Key('device_name', optional=True): t.String,
    t.Key('delete_on_termination', optional=True): t.Bool
    })


INSTANCE_INFO = t.Dict({
    t.Key('ebs_volumes'): t.List(EBS_VOLUME),
    t.Key('instance_type'): INSTANCE_TYPE,
    t.Key('ami'): t.String,  # YELLOW: regex validation
    t.Key('vpc_security_group_ids'): t.List(t.String),
    t.Key('count'): t.Int(gt=0, lt=100),
    t.Key('availability_zone'): t.String
    }).allow_extra('*').make_optional('*')


# YELLOW: add some common keys so we know what they should look like
APP_CONFIGURATION = t.Dict({
    t.Key('drenv_override'): GENERIC_DICT
    }).allow_extra('*').make_optional('*')


SERVER = t.Dict({
    t.Key('label'): t.String,
    t.Key('instance_info', optional=True): INSTANCE_INFO,
    t.Key('app_configuration', optional=True): APP_CONFIGURATION,
    t.Key('elb', optional=True): t.String,
    t.Key('route53_record', optional=True): t.String,
    t.Key('services', optional=True): t.List(t.String)
    }).allow_extra('*')


SECURITY_GROUP = t.Dict({
    t.Key('label'): t.String,
    t.Key('source'): t.String
    })


ELB = t.Dict({
    t.Key('label'): t.String,
    t.Key('route53_record', optional=True): t.String
    })


ROUTE53_RECORD = t.Dict({
    t.Key('label'): t.String,
    t.Key('public'): t.Bool
    })


GLOBAL_OPTIONS = t.Dict({
    t.Key('remote_user', optional=True): t.String
    })


LAYOUT = t.Dict({
    t.Key('servers'): t.List(SERVER),
    t.Key('security_groups', optional=True): t.List(SECURITY_GROUP),
    t.Key('elbs', optional=True): t.List(ELB),
    t.Key('route53_records', optional=True): t.List(ROUTE53_RECORD),
    t.Key('global_options', optional=True): GLOBAL_OPTIONS,
    }).allow_extra('*')
