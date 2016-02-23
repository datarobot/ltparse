#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click

from parser import load_layout, \
                   read_global_options, \
                   format_data, \
                   write_data, \
                   log
from validate import LAYOUT


@click.command(options_metavar='')
@click.argument('layout',
                type=click.File(mode='r'),
                metavar='layout')
@click.argument('output',
                type=click.Path(writable=True,
                                dir_okay=False,
                                resolve_path=True),
                metavar='[output]',
                required=False)
def cli(layout, output):
    """
    Read provided YAML-formatted layout and write a Terraform-compatible
    .tf.json file

    \b
    Parameters
    ----------
    layout:
        Path to a YAML layout file or - for stdin
    output:
        File to write instead of parsed.tf.json. Must end in .tf.json
    """
    if not output:
        output = 'parsed.tf.json'
    assert output.endswith('.tf.json'), 'Output filename must end in .tf.json'
    layout_data = load_layout(layout)
    LAYOUT.check(layout_data)
    read_global_options(layout_data)
    terraform_data = format_data(layout_data)
    write_data(terraform_data, output)
    log.debug('success')
