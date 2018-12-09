#!/usr/bin/env python
# -*- coding:utf-8 -*-
from copy import deepcopy

from util import unique


def used_material_names(gltf):
    """
    使用しているマテリアル名リストを取得
    :param gltf: glTFオブジェクト
    :return: 使用しているマテリアル名リスト
    """
    material_names = [primitive['material']['name'] for mesh in gltf['meshes'] for primitive in mesh['primitives']]
    return set(material_names)


def clean_gltf_materials(gltf):
    """
    未使用のglTFマテリアルを削除する
    :param gltf: glTFオブジェクト
    :return: 新しいマテリアルリスト
    """
    return filter(lambda m: m['name'] in used_material_names(gltf), gltf['materials'])


def clean_vrm_materials(gltf):
    """
    未使用のVRMマテリアルを削除する
    :param gltf: glTFオブジェクト
    :return: 新しいマテリアルリスト
    """
    # VRMマテリアル削除
    vrm = gltf['extensions']['VRM']
    return filter(lambda m: m['name'] in used_material_names(gltf), vrm['materialProperties'])


def list_textures(gltf):
    """
    使用中のテクスチャを列挙する
    :param gltf: glTFオブジェクト
    :return: テクスチャリスト(generator)
    """
    # GLTFテクスチャ
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
    """
    未使用テクスチャを削除したテクスチャリストを返す
    :param gltf: glTFオブジェクト
    :return: 新しいテクスチャリスト
    """
    return unique(list_textures(gltf))


def clean_images(gltf):
    """
    未使用画像を削除
    :param gltf: glTFオブジェクト
    :return: 新しい画像リスト
    """
    return map(lambda t: t['source'], gltf['textures'])


def clean_samplers(gltf):
    """
    未使用サンプラーを削除したサンプラーリストを返す
    :param gltf: glTFオブジェクト
    :return: 新しいサンプラーリスト
    """
    return map(lambda t: t['sampler'], gltf['textures'])


def list_accessors(gltf):
    """
    アクセサーを列挙する
    :param gltf: glTFオブジェクト
    :return: アクセッサー列挙(generator)
    """
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
    """
    未使用アクセッサーを削除したアクセッサーリストを返す
    :param gltf: glTFオブジェクト
    :return: 新しいアクセッサーリスト
    """
    return unique(list_accessors(gltf))


def list_buffer_views(gltf):
    # バッファビュー列挙
    for accessor in gltf['accessors']:
        yield accessor['bufferView']
        # TODO: sparse対応

    for image in gltf['images']:
        if 'bufferView' in image:
            yield image['bufferView']


def clean_buffer_views(gltf):
    """
    未使用バッファービューを削除したバッファービューリストを返す
    :param gltf: glTFオブジェクト
    :return: 新しいバッファービューリスト
    """
    return unique(list_buffer_views(gltf))


def clean(gltf):
    """
    不要なマテリアル、テクスチャ、画像、サンプラー、アクセッサー、バッファビューを削除する
    :param gltf: glTFオブジェクト
    :return: 削除後のglTFオブジェクト
    """
    gltf = deepcopy(gltf)

    # 未参照のマテリアルを削除
    gltf['materials'] = clean_gltf_materials(gltf)
    gltf['extensions']['VRM']['materialProperties'] = clean_vrm_materials(gltf)

    # 未参照のテクスチャを削除
    gltf['textures'] = clean_textures(gltf)

    # 未参照の画像を削除
    gltf['images'] = clean_images(gltf)

    # 未参照のサンプラーを削除
    gltf['samplers'] = clean_samplers(gltf)

    # 不要アクセッサーを削除
    gltf['accessors'] = clean_accesors(gltf)

    # 不要バッファービューを削除
    gltf['bufferViews'] = clean_buffer_views(gltf)

    return gltf
