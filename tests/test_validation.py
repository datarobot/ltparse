#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import trafaret

from ltparse.validate import (
        ABSOLUTE_PATH,
        INSTANCE_TYPE,
        LAYOUT
        )


@pytest.mark.parametrize('path', [
    '/a',
    '/0',
    '/a0',
    '/a\0',
    '/path',
    '/some/path',
    '/another/path/',
    '/path with spaces'
    ])
def test_absolute_path_good(path):
    """
    ABSOLUTE_PATH is a trafaret String with a regex meant to identify valid
    absolute paths for mounting additional EBS volumes. Therefore we accept
    any valid absolute path that isn't equivalent to the / path.
    """
    ABSOLUTE_PATH.check(path)


@pytest.mark.parametrize('path', [
    'a',
    '/\0',
    '/\0a',
    'path',
    'some/path',
    'another/path/',
    'path with spaces',
    '//',
    1,
    [],
    {},
    ])
def test_absolute_path_bad(path):
    """
    ABSOLUTE_PATH is a trafaret String with a regex meant to identify valid
    absolute paths for mounting additional EBS volumes. Therefore we accept
    any valid absolute path that isn't equivalent to the / path.
    """
    with pytest.raises(trafaret.DataError):
        ABSOLUTE_PATH.check(path)


@pytest.mark.parametrize('instance', [
    't2.nano',
    't2.micro',
    'm3.small',
    't2.medium',
    'c4.large',
    'r3.xlarge',
    'g2.2xlarge',
    'g2.8xlarge',
    'm4.10xlarge',
    ])
def test_instance_type_good(instance):
    """
    INSTANCE_TYPE is a trafaret String with regex validation meant to catch
    simple errors that could appear when creating layouts. While this will not
    catch all invalid types, such as t2.xlarge, it will ensure that most typos
    are avoided.
    """
    INSTANCE_TYPE.check(instance)


@pytest.mark.parametrize('instance', [
    't2.xnano',
    'z2.micro',
    'm5.small',
    't2.mdeium',
    'c0.large',
    'r3.xxlarge',
    'g2.0xlarge',
    'g2.5xlarge',
    'm4.11xlarge',
    'm4.210xlarge',
    'm3large',
    '',
    [],
    ['m3.large']
    ])
def test_instance_type_bad(instance):
    """
    INSTANCE_TYPE is a trafaret String with regex validation meant to catch
    simple errors that could appear when creating layouts. While this will not
    catch all invalid types, such as t2.xlarge, it will ensure that most typos
    are avoided.
    """
    with pytest.raises(trafaret.DataError):
        INSTANCE_TYPE.check(instance)


def test_good_layouts(test_layout):
    """
    Layouts are validated using the LAYOUT schema.
    """
    layout, _ = test_layout
    LAYOUT.check(layout)
