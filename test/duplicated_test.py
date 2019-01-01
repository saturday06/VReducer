#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pytest

from vrm.reducer import unique_vrm_materials, deduplicated_materials


@pytest.mark.parametrize(
    "src, dst", [
        (
                [
                    {'name': 'mat1', 'renderQueue': 3000, 'vectorProperties': {'_OutlineColor': [1, 1, 1, 1]}},
                    {'name': 'mat2', 'renderQueue': 3000, 'vectorProperties': {'_OutlineColor': [1, 1, 1, 1]}},
                    {'name': 'mat3', 'renderQueue': 1000, 'vectorProperties': {'_OutlineColor': [1, 1, 1, 1]}}
                ],
                {'mat1': 'mat1', 'mat2': 'mat1', 'mat3': 'mat3'}
        ),
        (
                [
                    {'name': 'mat1', 'renderQueue': 3000, 'vectorProperties': {'_OutlineColor': [1, 1, 1, 1]}},
                    {'name': 'mat2', 'renderQueue': 3000, 'vectorProperties': {'_OutlineColor': [0, 0, 0, 0]}},
                ],
                {'mat1': 'mat1', 'mat2': 'mat1'}
        ),
        ([], {})
    ]
)
def test_unique_materials(src, dst):
    assert dict(unique_vrm_materials(src)) == dst


@pytest.mark.parametrize(
    "src, dst", [
        (
                {
                    'extensions': {
                        'VRM': {
                            'materialProperties': [
                                {'name': 'mat1', 'vectorProperties': {'_OutlineColor': []}},
                                {'name': 'mat2', 'vectorProperties': {'_OutlineColor': []}},
                                {'name': 'mat3', 'vectorProperties': {'_OutlineColor': []}, 'renderQueue': 0}
                            ]
                        }
                    },
                    'materials': [{'name': 'mat1'}, {'name': 'mat2'}, {'name': 'mat3'}],
                    'meshes': [
                        {
                            'primitives': [
                                {'material': {'name': 'mat1'}}, {'material': {'name': 'mat2'}},
                                {'material': {'name': 'mat2'}}, {'material': {'name': 'mat3'}}
                            ]
                        }
                    ]
                },
                {
                    'extensions': {
                        'VRM': {
                            'materialProperties': [
                                {'name': 'mat1', 'vectorProperties': {'_OutlineColor': []}},
                                {'name': 'mat3', 'vectorProperties': {'_OutlineColor': []}, 'renderQueue': 0}
                            ]
                        }
                    },
                    'materials': [{'name': 'mat1'}, {'name': 'mat3'}],
                    'meshes': [
                        {
                            'primitives': [
                                {'material': {'name': 'mat1'}}, {'material': {'name': 'mat1'}},
                                {'material': {'name': 'mat1'}}, {'material': {'name': 'mat3'}}
                            ]
                        }
                    ]
                }
        ),
        (
                {
                    'extensions': {'VRM': {'materialProperties': []}},
                    'materials': [],
                    'meshes': [{'primitives': []}]
                },
                {
                    'extensions': {'VRM': {'materialProperties': []}},
                    'materials': [],
                    'meshes': [{'primitives': []}]
                }
        ),
        (
                {
                    'extensions': {'VRM': {'materialProperties': []}},
                    'materials': [],
                    'meshes': []
                },
                {
                    'extensions': {'VRM': {'materialProperties': []}},
                    'materials': [],
                    'meshes': []
                }
        )
    ]
)
def test_deduplicated_materials(src, dst):
    assert deduplicated_materials(src) == dst
