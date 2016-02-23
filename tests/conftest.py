#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import json
import os

import pytest
import yaml

from ltparse.utils import unicode_to_str


GOOD_INPUTS = sorted(glob.glob('tests/layouts/good/*.yaml'))


GOOD_OUTPUTS = sorted(glob.glob('tests/layouts/good/*.tf.json'))


BAD_INPUTS = sorted(glob.glob('tests/layouts/bad/*.yaml'))


@pytest.fixture(params=zip(GOOD_INPUTS, GOOD_OUTPUTS))
def test_layout(request):
    """
    Read in example layouts and corresponding verified outputs, return parsed
    dicts for use in various unit tests.
    """
    layout_file_name, output_file_name = request.param

    with open(layout_file_name, 'r') as f:
        layout = yaml.load(f.read())

    with open(output_file_name, 'r') as f:
        output = unicode_to_str(json.loads(f.read()))

    return layout, output


@pytest.fixture(params=BAD_INPUTS)
def test_bad_layout(request):
    """
    Fixture for negative case handling. Read in layouts with bad configs so we
    can make assertions on how we handle misconfiguration.
    """
    with open(request.param, 'r') as f:
        return yaml.load(f.read())


DICT_UPDATE_CASES = \
    [
        # Accepts empty dicts
        {
            'orig': {},
            'mod': {},
            'expect': {}
        },
        # Adds new key value pairs
        {
            'orig': {},
            'mod': {'foo': 'bar'},
            'expect': {'foo': 'bar'}
        },
        # Basic item replacement
        {
            'orig': {'foo': 'bar'},
            'mod': {'foo': 'baz'},
            'expect': {'foo': 'baz'}
        },
        # Updates singly nested dict
        {
            'orig': {'foo': {'bar': 'baz'}},
            'mod': {'foo': {'bar': 'asdf'}},
            'expect': {'foo': {'bar': 'asdf'}}
        },
        # Updates doubly nested dict
        {
            'orig': {'foo': {'bar': {'baz': 'biz'}}},
            'mod': {'foo': {'bar': {'baz': 'asdf'}}},
            'expect': {'foo': {'bar': {'baz': 'asdf'}}}
        },
        # Doesn't merge lists
        {
            'orig': {'foo': ['bar', 'baz']},
            'mod': {'foo': ['asdf']},
            'expect': {'foo': ['asdf']}
        },
        # Merges dicts
        {
            'orig': {'cats': 'meow'},
            'mod': {'dogs': 'woof'},
            'expect': {'cats': 'meow', 'dogs': 'woof'}
        },
        # Merges nested dicts
        {
            'orig': {'cats': {'sound': 'meow'}},
            'mod': {'cats': {'fur': 'soft'}},
            'expect': {'cats': {'sound': 'meow', 'fur': 'soft'}}
        },
        # Replaces string with dict
        {
            'orig': {'foo': 'bar'},
            'mod': {'foo': {'bar': 'baz'}},
            'expect': {'foo': {'bar': 'baz'}}
        },
        # Replaces dict with string
        {
            'orig': {'foo': {'bar': 'baz'}},
            'mod': {'foo': 'bar'},
            'expect': {'foo': 'bar'}
        },
        # Merges dict into nested dict at the right level
        {
            'orig': {'foo': 'bar', 'baz': {'biz': 'buz'}},
            'mod': {'cats': 'meow'},
            'expect': {'foo': 'bar', 'cats': 'meow', 'baz': {'biz': 'buz'}},
        },
    ]


@pytest.fixture(params=DICT_UPDATE_CASES)
def test_dict(request):
    """
    Fixture for testing update_recursive functionality.
    """
    return request.param
