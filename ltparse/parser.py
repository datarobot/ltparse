#!/usr/bin/env python
import copy
import logging as log
import yaml

from defaults import DEFAULT_INSTANCE, \
                     DEFAULT_SECURITY_GROUP, \
                     DEFAULT_ELB, \
                     DEFAULT_ROUTE53_RECORD
import utils


log.basicConfig(level=log.INFO)

# placeholder for the global_options dict that we read from the layout file
# This lets us refer to the options globally
GLOBAL_OPTIONS = {
        'remote_user': 'ubuntu'
        }


class ConfigurationError(Exception):
    pass


def load_layout(layout):
    return utils.unicode_to_str(yaml.load(layout))


def _get_drive_letter(index):
    """
    convert index to drive letter, starting from 'f'

    'f' is chosen to allow enough room for extra drives in the normal a,b,c,d
    naming scheme

    ensures unique drive letters for each EBS volume added

    Takes index (integer in [0 - 20]) and returns corresponding character
    [f - z]
    """
    if not isinstance(index, int):
        raise TypeError('Invalid type for index. Expected int, got {}'
                        .format(type(index)))

    if index < 0 or index > 20:
        raise ValueError(
                'Invalid drive index specified. Expected [0 - 20], got {}'
                .format(index))

    return chr(ord('f') + index)


def _get_ebs_block_devices(extra_info):
    """
    Read info for EBS block devices and return a dict (empty if no vols)

    extra_info comes from instance_info in layout file

    Return dict is of format { 'ebs_block_device': ebs_volumes }
    where ebs_volumes is a list of dicts specifying EBS volumes.
    """
    volumes = extra_info.get('ebs_volumes', [])
    ebs_volumes = []
    for index, volume in enumerate(volumes):
        vol = copy.deepcopy(volume)
        # volume_size is the only required parameter
        try:
            vol['volume_size']
        except KeyError:
            raise ConfigurationError(
                    'Missing volume_size parameter in ebs_volumes list.')
        if not vol.get('volume_size'):
            raise ConfigurationError(
                    'Invalid volume_size parameter in ebs_volumes list. '
                    'Got {}.'.format(vol['volume_size']))

        device_name = vol.get('device_name')
        if not device_name:
            device_name = '/dev/xvd{}'.format(_get_drive_letter(index))
            vol.update({'device_name': device_name})

        # mountpoint is not a valid Terraform key
        # We use the parameter to mount it in the provisioner step
        try:
            vol.pop('mountpoint')
        except KeyError:
            pass
        ebs_volumes.append(vol)
    if ebs_volumes:
        return {'ebs_block_device': ebs_volumes}
    return {}


def _get_provisioners(extra_info, label):
    """
    Read extra info for server and return any necessary provisioners

    Provisioners that might be added:
      EBS mkfs and mount (if EBS devices added)
    """
    provisioners = []
    # YELLOW: this line seems a little silly
    # But it does mean you can run this function without first running
    # _get_ebs_block_device, which makes things a little less implicit
    block_devices = _get_ebs_block_devices(extra_info).get('ebs_block_device',
                                                           [])
    for index, vol in enumerate(block_devices):
        mountpoint = extra_info['ebs_volumes'][index].get('mountpoint')
        device_name = vol['device_name']
        if mountpoint:
            provisioner = {
                    'remote-exec': {
                        'inline': [
                            'sudo mkfs -F -t ext4 {}'.format(device_name),
                            'sudo mount {} {}'.format(device_name, mountpoint)
                            ],
                        'connection': {
                            'user':
                                GLOBAL_OPTIONS['remote_user'],
                            'private_key':
                                '${file("${var.aws.your_key_path}")}',
                            'host':
                                '${{aws_instance.{}.private_ip}}'.format(label)
                            }
                        }
                    }
            provisioners.append(provisioner)
        else:
            log.warn('EBS volume {} specified without mountpoint on label {}. '
                     'The volume will not be formatted or mounted. {}'.format(
                         device_name, label, mountpoint))

    if provisioners:
        return {'provisioner': provisioners}
    return {}


def _get_instance_security_groups(extra_info):
    """
    Take common names of security groups, if any specified, and construct
    Terraform dictionaries using the module state to identify the group.

    If none are specified in the layout the default in defaults.py will be
    used.
    """
    requested_security_groups = extra_info.get('security_groups', [])
    security_groups = []
    for security_group in requested_security_groups:
        security_groups.append('${module.' + security_group + '.id}')

    if security_groups:
        return {'vpc_security_group_ids': security_groups}
    return {}


def _filter_info(info):
    """
    Remove keys from the extra info dict that cannot go straight into Terraform
    """
    filtered = copy.deepcopy(info)

    try:
        filtered.pop('ebs_volumes')
    except KeyError:
        pass

    return filtered


def _add_instance(server):
    """
    Given a server dict from the layout, merge configuration from the YAML into
    the defaults provided in defaults.py.

    Returns a dict that looks like {label: data}
    """
    try:
        label = server['label']
    except KeyError:
        raise ConfigurationError('Server without a label encountered! '
                                 'Data was:\n'
                                 '{}'.format(utils.dump_yaml(server)))

    # Apply extra config from yaml file
    extra_info = server.get('instance_info', {})
    filtered_info = _filter_info(extra_info)
    instance_data = utils.update_recursive(DEFAULT_INSTANCE, filtered_info)
    log.debug(utils.dump_json(instance_data))

    # Logic for special cases
    az = extra_info.get('availability_zone', 'us-east-1a')
    instance_data['subnet_id'] = \
        '${{terraform_remote_state.subnets.output.{}}}'.format(az)

    instance_data['tags'].update({'label': label})
    instance_data['tags'].update({'id': label + '_${var.run_id}'})

    ebs_data = _get_ebs_block_devices(extra_info)
    log.debug(utils.dump_json(ebs_data))
    instance_data.update(ebs_data)

    provisioners = _get_provisioners(extra_info, label)
    log.debug(utils.dump_json(provisioners))
    instance_data.update(provisioners)

    security_groups = _get_instance_security_groups(extra_info)
    log.debug(utils.dump_json(security_groups))
    instance_data.update(security_groups)

    return {label: instance_data}


def add_instances(data):
    instances = {}
    data = copy.deepcopy(data)

    try:
        servers = data['servers']
    except KeyError:
        raise ConfigurationError('No "servers" list in layout')

    for server in servers:
        instances.update(_add_instance(server))

    return {'aws_instance': instances}


def add_elbs(data):
    new_data = {}
    for elb in data.get('elbs', []):
        label = elb['label']
        instances = []
        for instance in data['servers']:
            # YELLOW:
            # This doesn't work if count > 1
            if instance.get('elb') == label:
                instances.append(
                    '${{aws_instance.{}.id}}'.format(instance['label']))
        assert len(instances) > 0, '\n'.join([
                'ELB {label} specified but no instances attached.'.format(
                    label=label),
                'use `elb: {label}` in a server definition '
                'to add it to this ELB'.format(label=label)])
        new_data[label] = copy.deepcopy(DEFAULT_ELB)
        new_data[label]['instances'] = instances
    if new_data:
        return {'aws_elb': new_data}
    return {}


def add_route53_records(data):
    new_data = {}
    for record in data.get('route53_records', []):
        label = record['label']
        instances = []
        for instance in data['servers']:
            # YELLOW:
            # This doesn't work if count > 1
            if instance.get('route53_record') == label:
                if record.get('public', False):
                    instances.append('${{aws_instance.{}.public_ip}}'.format(
                        instance['label']))
                else:
                    instances.append('${{aws_instance.{}.private_ip}}'.format(
                        instance['label']))
        elbs = []
        for elb in data.get('elbs', []):
            if elb.get('route53_record') == label:
                elbs.append('${aws_elb.' + elb['label'] + '.dns_name}')
        if instances and elbs:
            raise ConfigurationError(
                    'route53 record label `{}` applied to both instances and '
                    'an elb.'.format(label))
        if not (instances or elbs):
            raise ConfigurationError(
                    'route53 record label `{}` not applied to any instances '
                    'or elbs'.format(label))
        new_data[label] = copy.deepcopy(DEFAULT_ROUTE53_RECORD)
        if elbs:
            new_data[label]['type'] = 'CNAME'
        new_data[label]['records'] = instances + elbs
        new_data[label]['name'] = '${{var.run_id}}-{}'.format(
                label)
    if new_data:
        return {'aws_route53_record': new_data}
    return {}


def add_security_groups(data):
    new_data = {}
    data = copy.deepcopy(data)
    security_groups = data.get('security_groups', [])
    security_groups.append(DEFAULT_SECURITY_GROUP)
    for group in security_groups:
        group.update({'run_id': '${var.run_id}'})
        group.update({'vpc_id': '${var.aws.vpc_id}'})
        new_data.update({group['label']: group})
    return new_data


def format_data(data):
    new_data = {}

    new_data['provider'] = {'aws': {'region': '${var.aws.region}'}}
    new_data['variable'] = {'run_id': {}}
    new_data['module'] = add_security_groups(data)
    new_data['resource'] = {}
    new_data['resource'].update(add_instances(data))
    new_data['resource'].update(add_elbs(data))
    new_data['resource'].update(add_route53_records(data))

    return utils.unicode_to_str(new_data)


def write_data(data, dest):
    with open(dest, 'w') as f:
        f.write(utils.dump_json(data))


def read_global_options(data):
    GLOBAL_OPTIONS.update(data.get('global_options', {}))
