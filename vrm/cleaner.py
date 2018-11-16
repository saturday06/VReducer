#!/usr/bin/env python
# -*- coding:utf-8 -*-
from copy import deepcopy

from util import unique


def clean_materials(gltf):
    # 未使用マテリアルを削除
    gltf = deepcopy(gltf)

    # 使用しているマテリアル名列挙
    material_names = [primitive['material']['name'] for mesh in gltf['meshes'] for primitive in mesh['primitives']]
    material_names = set(material_names)

    # GLTFマテリアル削除
    gltf['materials'] = filter(lambda m: m['name'] in material_names, gltf['materials'])

    # VRMマテリアル削除
    vrm = gltf['extensions']['VRM']
    vrm['materialProperties'] = filter(lambda m: m['name'] in material_names, vrm['materialProperties'])

    return gltf


def list_textures(gltf):
    # GTLFテクスチャ
    for material in gltf['materials']:
        if 'baseColorTexture' in material['pbrMetallicRoughness']:
            yield material['pbrMetallicRoughness']['baseColorTexture']['index']
        for tex_name in ['normalTexture', 'emissiveTexture']:
            if tex_name in material:
                yield material[tex_name]['index']

    # VRMテクスチャ
    vrm = gltf['extensions']['VRM']
    for material in vrm['materialProperties']:
        for texture in material['textureProperties'].values():
            yield texture
    yield vrm['meta']['texture']


def clean_textures(gltf):
    # 未使用テクスチャを削除
    gltf = deepcopy(gltf)
    gltf['textures'] = unique(list_textures(gltf))
    return gltf


def clean_images(gltf):
    # 未使用画像を削除
    gltf = deepcopy(gltf)
    gltf['images'] = map(lambda t: t['source'], gltf['textures'])
    return gltf


def clean_samplers(gltf):
    # 未使用サンプラを削除
    gltf = deepcopy(gltf)
    gltf['samplers'] = map(lambda t: t['sampler'], gltf['textures'])
    return gltf


def list_accessors(gltf):
    # アクセサーを列挙
    for skin in gltf['skins']:
        yield skin['inverseBindMatrices']

    for mesh in gltf['meshes']:
        for primitive in mesh['primitives']:
            yield primitive['indices']
            for attr_value in primitive['attributes'].values():
                yield attr_value
            if 'targets' in primitive:
                for target in primitive['targets']:
                    for target_value in target.values():
                        yield target_value


def clean_accesors(gltf):
    # 未使用アクセッサーを削除
    gltf = deepcopy(gltf)
    gltf['accessors'] = unique(list_accessors(gltf))
    return gltf


def list_buffer_views(gltf):
    # バッファビュー列挙
    for accessor in gltf['accessors']:
        yield accessor['bufferView']
        # TODO: sparse対応

    for image in gltf['images']:
        if 'bufferView' in image:
            yield image['bufferView']


def clean_buffer_views(gltf):
    # 未使用バッファービューを削除
    gltf = deepcopy(gltf)
    gltf['bufferViews'] = unique(list_buffer_views(gltf))
    return gltf


def clean(gltf):
    # 未参照のマテリアルを削除
    gltf = clean_materials(gltf)

    # 未参照のテクスチャを削除
    gltf = clean_textures(gltf)

    # 未参照の画像を削除
    gltf = clean_images(gltf)

    # 未参照のサンプラーを削除
    gltf = clean_samplers(gltf)

    # 不要アクセッサーを削除
    gltf = clean_accesors(gltf)

    # 不要バッファービューを削除
    gltf = clean_buffer_views(gltf)

    return gltf
