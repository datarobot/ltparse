#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

from ltparse.utils import update_recursive


def test_update_recursive_cases(test_dict):
    """
    For each case in conftest.DICT_UPDATE_CASES, assert that the function
    behaves as expected.
    """
    original = test_dict['orig']
    original_copy = copy.deepcopy(original)
    mod = test_dict['mod']
    expected = test_dict['expect']
    new = update_recursive(original, mod)
    assert original == original_copy
    assert new == expected
