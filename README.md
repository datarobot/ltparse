# Flexible layouts parser

This tool (`ltparse`) exists to read in human-readable YAML layout files (see `tests/layouts/good/`) and produces a `.tf.json` file that Terraform can use to create infrastructure.
The layout files can also be read by other tools to provision servers with code and services, for example by using `container-from-compose`.

Simply put, it takes servers defined in the layout file and default Terraform options in
`defaults.py` and intelligently combines the two.

The result is a very flexible tool that lets the user add almost arbitrary levels of configuration
to their YAML file, or none at all beyond labels and services. For example, one server definition
might look like

```yaml
# minimal configuration
- label: worker
  services:
  - worker
```

while another might inject Terraform parameters that the parser tool passes through to Terraform:

```yaml
- label: webserver
  services:
  - nginx
  - app
  instance_info:
    iam_instance_profile: webserver
```

For more examples, check the layouts directory.

## Usage

The parser script takes one argument, which is the layouts file to use. The tool writes a file
called `parsed.tf.json` in the working directory. The Makefile wraps common commands.

```bash
mkvirtualenv ltparse
make install # use make develop to install editable
make plan
run_id=<run_id> make apply
```

## Testing

This project has a test suite you can run using `make test`. Because it has no CI set up so far, please run this before submitting contributions.

Unit tests are run using setuptools with the pytest test runner.

For end-to-end tests, use `make test-end2end`. This will run `make plan` using every layout in the
`layouts/` directory. Please make sure this succeeds before any merges.

### Note on unit tests
In order to make test writing easy, many unit tests use the `test\_layout` fixture, which returns dictionaries for example layouts tupled with the expected .tf.json output.
The .tf.json example outputs were created with the parser tool and manually inspected for correctness, as well as run through `terraform plan`.
For each function that takes in data from the layout and produces a piece of the Terraform data, there should be a test that verifies that each possible layout input from the `tests/layouts/good` directory produces the expected and verified output, and that improper layouts from the `tests/layouts/bad` produce errors.

Note that for each bad layout, you must specify an additional key: value pair of the form `expects: <exception type> <message>` (see existing bad layouts for examples).
The function `test\_full\_layouts\_bad` and tests of particular functions will ensure that parsing misconfigured layouts will produce the expected messages.

## Layout specifications

As mentioned, layouts can be extremely simple. A minimal example exists in `layouts/minimal.yaml`.
However, the real power comes when you start using advanced features.

### Required parameters
The root level of the layout must have the key `servers`, which is a list of dictionaries. Each
element of this dictionary must have a `label` key which uniquely identifies this item in the
list. The `services` list is technically optional; `parser.py` ignores this field; but why are you
launching servers without services?

### Optional server parameters
Each dictionary in the servers list can also have an `instance\_info` dict. Any valid parameter for the
Terraform `aws\_instance` resource can be put here. The defaults in `defaults.py`, if they exist, will
be overriden by these values.

However, there are two special cases. The first is `ebs\_volumes`, which contains an extra key not
present in the Terraform `ebs\_block\_device` section of the `aws\_instance`. This key is `mountpoint`
and is handled specially to configure a provisioner that makes a file system and mounts the
specified EBS volume. `volume\_size` is the only required parameter for this dict, but you probably
also want `mountpoint` so that the volume gets mounted.

The second is the `vpc\_security\_group\_ids` list. Rather than writing
`${modules.my\_security\_group.id}` in the layout for each security group, you can use the friendly
names and the parser will take care of parsing it for Terraform.

### Resources that aren't instances

In addition to creating instances, this tool currently supports basic security groups (write your
own modules and use them if you like!), ELB's, and route53 records. Each must have a label, which
is used in naming the resource and in referencing it in other parts of the layout.

For example, the following snippet will create a server that is in a public-facing security group,
in an ELB, and has a route53 record of `$run\_id-webserver.my.domain.com` pointed to its private
IP address:

```yaml
servers:
- label: webserver
  services:
  - app
  - nginx
  route53_record: webserver # tells parser to add the webserver record to this instance
  elb: webserver # tells parser to add this instance to this ELB
  instance_info:
    vpc_security_group_ids:
    - public_security_group
    - default_security_group

route53_records:
- label: webserver
  domain: my.domain.com

elbs:
- label: webserver
```

#### Security groups
To create a security group, write a module or use an existing one. Then in your layout, put

```yaml
security_groups:
- label: my_sg
  source: modules/sgs/my_sg
```
The label is part of security group's name and is used to reference the security group in ELB's or
instances.

#### ELB
ELB defaults are specified in `defaults.py` and any of them can be overridden from the layout file.

Currently only internal ELB's are supported.

#### Route53
Currently only records that point to a private IP or ELB are supported.

## High-level plan for this project

This tool is intended to replace the Ansible and Python-based launch system we currently use for
test clusters, since it can give us more reliability and greater flexibility.
