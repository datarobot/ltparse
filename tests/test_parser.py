import copy

import pytest

from ltparse.parser import (
        _get_drive_letter,
        _get_ebs_block_devices,
        format_data,
        ConfigurationError
        )


@pytest.mark.parametrize('index,expected', [
    (0, 'f'),
    (1, 'g'),
    (5, 'k'),
    (20, 'z')
    ])
def test_get_drive_letter(index, expected):
    """
    Ensure valid values for get_drive_letter produce expected results
    """
    letter = _get_drive_letter(index)
    assert letter == expected


@pytest.mark.parametrize('index', [-1, 21])
def test_get_drive_letter_exceptions(index):
    """
    Ensure that get_drive_letter raises errors on invalid values.
    """
    with pytest.raises(ValueError):
        letter = _get_drive_letter(index)


@pytest.mark.parametrize('index', ['f', {}, '1', []])
def test_get_drive_letter_exceptions(index):
    """
    Ensure that get_drive_letter raises errors for invalid types
    """
    with pytest.raises(TypeError):
        letter = _get_drive_letter(index)


def test_get_ebs_block_devices(test_layout):
    """
    For each layout, output pair in tests/layouts/good, assert that running
    _get_ebs_block_devices formats the layout data into the expected EBS output
    and does not modify the original input data.
    """
    layout, output = test_layout
    for server in layout['servers']:
        label = server['label']
        expected_server = output['resource']['aws_instance'][label]
        extra_info = server.get('instance_info', {})
        extra_info_original = copy.deepcopy(extra_info)
        volumes = _get_ebs_block_devices(extra_info).get('ebs_block_device')
        expected_volumes = expected_server.get('ebs_block_device')
        assert extra_info == extra_info_original
        assert volumes == expected_volumes


def test_full_layouts(test_layout):
    """
    For each layout, output pair in tests/layouts/good, assert that running
    format_data formats the layout data into the expected output and does not
    modify the original input data.
    """
    layout, output = test_layout
    layout_orig = copy.deepcopy(layout)
    formatted = format_data(layout)
    assert layout == layout_orig
    assert formatted == output


def test_full_layouts_bad(test_bad_layout):
    """
    For each layout in tests/layouts/bad, assert that running format_data fails
    with the exception and message defined in the layout.
    """
    expected_exception = test_bad_layout['expects']
    with pytest.raises(type(expected_exception)) as excinfo:
        format_data(test_bad_layout)
    assert expected_exception.message == str(excinfo.value)
