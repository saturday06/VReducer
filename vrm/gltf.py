#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from copy import deepcopy

from version import app_name


def remove_instance(name):
    if '(Instance)' not in name:
        return name
    return name[:-11]  # 末尾の(Instance)表記を削除


def remove_clone(name):
    return name.replace('(Clone)', '')  # (Clone)表記を削除


def normalize_material_name(name):
    # マテリアル名についている余分な名前を削除する
    return remove_clone(remove_instance(name))


def instancing(gltf, chunks=None):
    """
    インデックス番号による参照をインスタンスデータへの直接参照に変換する
    :param gltf: glTFオブジェクト
    :param chunks: チャンクデータリスト
    :return: 変換後のglTFオブジェクト
    """
    gltf = deepcopy(gltf)

    accessors = gltf['accessors']
    materials = gltf['materials']
    buffer_views = gltf['bufferViews']

    # accessorsのbufferViewをインスタンス参照に更新
    for accessor in accessors:
        accessor['bufferView'] = buffer_views[accessor['bufferView']]

    meshes = gltf['meshes']
    for mesh in meshes:
        primitives = mesh['primitives']
        for primitive in primitives:
            primitive['indices'] = accessors[primitive['indices']]
            attributes = primitive['attributes']
            primitive['material'] = materials[primitive['material']]
            for name in attributes:
                attributes[name] = accessors[attributes[name]]
            if 'targets' in primitive:
                targets = primitive['targets']
                for target in targets:
                    for name in target:
                        target[name] = accessors[target[name]]

    skins = gltf['skins']
    for skin in skins:
        skin['inverseBindMatrices'] = accessors[skin['inverseBindMatrices']]

    # 画像変換
    images = gltf['images']
    for image in images:
        if 'bufferView' in image:
            image['bufferView'] = buffer_views[image['bufferView']]

    # テクスチャ変換
    samplers = gltf['samplers']
    textures = gltf['textures']
    for texture in textures:
        texture['source'] = images[texture['source']]
        texture['sampler'] = samplers[texture['sampler']]

    # 材質テクスチャ変換
    for material in materials:
        material['name'] = normalize_material_name(material['name'])  # マテリアル名を正規化

        pbr = material['pbrMetallicRoughness']
        for name in ['baseColorTexture', 'metallicRoughnessTexture']:
            if name in pbr:
                texture = pbr[name]
                texture['index'] = textures[texture['index']]

        for name in ['normalTexture', 'occulusionTexture', 'emissiveTexture']:
            if name in material:
                texture = material[name]
                texture['index'] = textures[texture['index']]

    # VRMテクスチャ変換
    vrm = gltf['extensions']['VRM']
    vrm['meta']['texture'] = textures[vrm['meta']['texture']]
    vrm_materials = vrm['materialProperties']
    for material in vrm_materials:
        material['name'] = normalize_material_name(material['name'])  # マテリアル名を正規化
        properties = material['textureProperties']
        for name in properties:
            properties[name] = textures[properties[name]]

    # マテリアル結合時に髪のマテリアルを区別できるように末尾に番号をつける
    # 一時的な変更、ファイル保存には元の名前に戻す
    for n, (material, vrm_material) in enumerate(zip(materials, vrm_materials)):
        material['name'] = vrm_material['name'] = '{}-{:02d}'.format(material['name'], n)

    if not chunks:
        # TODO: buffer URI
        return gltf

    # bufferViewにchunkデータをcontentとして設定
    for buffer_view in buffer_views:
        offset = buffer_view['byteOffset']
        length = buffer_view['byteLength']
        chunk = chunks[buffer_view['buffer']]
        buffer_view['data'] = chunk[offset:][:length]

    return gltf


def indexing(gltf):
    """
    参照をインデックス番号に戻す
    :param gltf: glTFオブジェクト
    :return: 変換後のglTFオブジェクト
    """
    gltf = deepcopy(gltf)

    # bufferをchunkに戻す
    buffer_views = gltf['bufferViews']

    # bufferViewからchunkを生成
    chunk = ''
    offset = 0
    for buffer_view in buffer_views:
        data = buffer_view.pop('data')
        data = data.ljust((len(data) + 3) / 4 * 4, '\0') # 4バイトアラインメント
        length = len(data)
        buffer_view['buffer'] = 0  # 1バッファにまとめるのでインデックスは0
        buffer_view['byteOffset'] = offset
        buffer_view['byteLength'] = length
        chunk += data
        offset += length
    gltf['buffers'] = [{'byteLength': len(chunk)}]
    chunks = [chunk]

    # bufferViewインデックスに戻す
    accessors = gltf['accessors']
    for accessor in accessors:
        accessor['bufferView'] = buffer_views.index(accessor['bufferView'])

    images = gltf['images']
    for image in images:
        if 'bufferView' in image:
            image['bufferView'] = buffer_views.index(image['bufferView'])

    # accessorインデックス、materialインデックスに戻す
    meshes = gltf['meshes']
    materials = gltf['materials']
    for mesh in meshes:
        primitives = mesh['primitives']
        for primitive in primitives:
            primitive['indices'] = accessors.index(primitive['indices'])
            attributes = primitive['attributes']
            primitive['material'] = materials.index(primitive['material'])
            for name in attributes:
                attributes[name] = accessors.index(attributes[name])
            if 'targets' in primitive:
                targets = primitive['targets']
                for target in targets:
                    for name in target:
                        target[name] = accessors.index(target[name])

    skins = gltf['skins']
    for skin in skins:
        skin['inverseBindMatrices'] = accessors.index(skin['inverseBindMatrices'])

    samplers = gltf['samplers']
    textures = gltf['textures']

    # 材質テクスチャ変換
    materials = gltf['materials']
    for material in materials:
        pbr = material['pbrMetallicRoughness']
        for name in ['baseColorTexture', 'metallicRoughnessTexture']:
            if name in pbr:
                texture = pbr[name]
                texture['index'] = textures.index(texture['index'])
        for name in ['normalTexture', 'occulusionTexture', 'emissiveTexture']:
            if name in material:
                texture = material[name]
                texture['index'] = textures.index(texture['index'])

    # VRMシェーダーテクスチャ変換
    vrm = gltf['extensions']['VRM']
    vrm['meta']['texture'] = textures.index(vrm['meta']['texture'])

    vrm_materials = vrm['materialProperties']
    for material in vrm_materials:
        properties = material['textureProperties']
        for name in properties:
            properties[name] = textures.index(properties[name])

    for texture in textures:
        texture['source'] = images.index(texture['source'])
        texture['sampler'] = samplers.index(texture['sampler'])

    # マテリアル名を戻す
    replace_reg = re.compile(r'(.+)-\d+')
    for n, (material, vrm_material) in enumerate(zip(materials, vrm_materials)):
        material['name'] = vrm_material['name'] = replace_reg.sub(r'\1', material['name'])

    # Exporter名を変更
    vrm['exporterVersion'] = app_name()

    return gltf, chunks
