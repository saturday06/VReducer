#!/usr/bin/env python
# -*- coding: utf-8 -*-


def print_stat(gltf):
    """
    モデル情報表示
    :param gltf: glTFオブジェクト
    """
    vrm = gltf['extensions']['VRM']
    print 'vrm materials:', len(vrm['materialProperties'])
    print 'materials:', len(gltf['materials'])
    print 'textures:', len(gltf['textures'])
    print 'images:', len(gltf['images'])

    meshes = gltf['meshes']
    print 'meshes:', len(meshes)
    print 'primitives:', sum([len(m['primitives']) for m in meshes])
    for mesh in meshes:
        print '\t', mesh['name'], ':', len(mesh['primitives'])
