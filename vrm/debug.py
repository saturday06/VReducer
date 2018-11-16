#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import groupby

"""
glTF仕様
チートシート：https://github.com/randall2835/gltfOverviewJapanese
パラメータ一覧；https://github.com/mebiusbox/gltf
"""


def display(gltf):
    print 'GLTF:'
    # GLTFファイルバージョン、エクスポーター情報
    print 'asset:', gltf['asset']
    # GLTFルート
    print 'scene:', gltf['scene']
    # nodes: シーンのルートノードリスト
    print 'scenes nodes', gltf['scenes']
    # シーンを構成するノード
    print 'nodes length:', len(gltf['nodes'])
    for n, node in enumerate(gltf['nodes'][:3]):
        # ノードで構成刺されるツリー構造を持る
        # ノードのローカル座標はツリー構造に沿ってノード変換行列を辿って演算した行列になる(M=T*R*S)
        # ボーン(ジョイント)情報も含む
        # name: ノード名
        # mesh: メッシュインデックス
        # skin: スキン情報インデックス
        # 行列：scale, translation, rotation
        # children: 子ノードのインデックスリスト
        # (camera: カメラインデックス)
        print '\tnode[{}]:'.format(n), node

    # テクスチャの画像とサンプラーのインデックスセットリスト
    print 'textures:'
    textures = gltf['textures']
    for n, texture in enumerate(textures):
        print '\ttexture[{}]:'.format(n), texture

    # テクスチャ画像
    print 'images:'
    for n, image in enumerate(gltf['images']):
        print '\timage[{}]:'.format(n)
        for key in image:
            print '\t\t{}:'.format(key), image[key]

    # テクスチャサンプラー
    print 'samplers:'
    for n, sampler in enumerate(gltf['samplers']):
        print '\timage[{}]:'.format(n), sampler

    # マテリアル
    print 'material:', gltf['materials'][0]

    # バッファ一覧(サイズとファイルへのURI)
    print 'buffers:', gltf['buffers']
    # バッファ内のサブセット領域
    for n, buffer_view in enumerate(gltf['bufferViews'][:2]):
        # buffer: バッファ一覧の対象バッファインデックス
        # byteLength: 領域サイズ
        # byteStride: データ開始位置の間隔(先頭バイト位置の間隔のこと)
        # target: GLバッファタイプ(ARRAY_BUFFER=34962, ELEMENT_ARRAY_BUFFER=34963
        print '\tbuffer-view[{}]:'.format(n), buffer_view

    # バッファデータの型情報とサイズ
    print 'accessors length:', len(gltf['accessors'])
    for n, accessor in enumerate(gltf['accessors'][:2]):
        # count:
        # bufferView: 対象バッファビューインデックス
        # byteOffset: バッファビュー上のバイトオフセット
        # componentType: データ型
        # BYTE= 5120, UNSIGNED_BYTE = 5121, SHORT = 5122. UNSIGNED_SHORT = 5123
        # INT=5124, UNSIGNED_INT= 5125, FLOAT = 5126
        # type: ベクトル型 (SCALAR, VEC2, VEC3, VEC4, MAT2, MAT3, MAT4)
        # min, max: FLOAT値の範囲
        print '\taccessor[{}]:'.format(n)
        for key in accessor:
            print '\t\t{}:'.format(key), accessor[key]

    # メッシュ(プリミティブ情報)
    for mesh in gltf['meshes']:
        print 'name:', mesh['name']
        # プリミティブリスト
        print 'primitives length:', len(mesh['primitives'])
        for primitive in mesh['primitives'][:1]:
            # ポリゴンの描画モード
            print '\tmode:', primitive['mode']
            # 頂点インデックスへのアクセッサーのインデックス
            print '\tindices:', primitive['indices']
            # 頂点属性(番号はアクセッサーのインデックス)
            print '\tattributes:', primitive['attributes']
            # マテリアルインデックス
            print '\tmaterial:', primitive['material']
            if 'targets' in primitive:
                # モーフの変位量と変位属性情報(番号はアクセッサーのインデックス)
                print '\ttargets length:', len(primitive['targets'])
                for target in primitive['targets'][:1]:
                    print '\t\tmorph target:', target
            if 'extras' in primitive:
                # モーフ名(VRM拡張情報)
                print '\tmorph name:', primitive['extras']['targetNames'][:2]

    # スキン情報
    print 'skins length:', len(gltf['skins'])
    for skin in gltf['skins']:
        # joints: ジョイントノードのインデックスリスト
        # inverseBindMatrices: 各ジョイントの逆バインド行列のアクセッサーインデックス
        # skin; ルートノードインデックス
        print '\tjoints length:', len(skin['joints'])
        for key in skin:
            print '\t{}:'.format(key), skin[key]


def display_vrm(gltf):
    vrm = gltf['extensions']['VRM']
    print 'extensions:'
    # 揺れるボーンと当たり判定情報
    secondary_anim = vrm['secondaryAnimation']
    print 'secondaryAnimation:'
    print '\tboneGroups:'
    bone_groups = secondary_anim['boneGroups']
    for bone_group in bone_groups:
        for key in bone_group:
            print '\t\t{}:'.format(key), bone_group[key]
    colliders = secondary_anim['colliderGroups']
    for collider in colliders:
        print collider

    # VRMエクスポーターバージョン
    print 'exporterVersion:', vrm['exporterVersion']
    print 'materialProperties:'
    vrm_materials = vrm['materialProperties']
    for material in vrm_materials[:1]:
        # 材質のシェーダーパラメータ
        print '\tmaterial name:', material['name']
        print '\tmaterial shader:', material['shader']
        print '\tmaterial renderQueue:', material['renderQueue']
        print '\tmaterial floatProperties:', material['floatProperties']
        print '\tmaterial vectorProperties:'
        vector_props = material['vectorProperties']
        for prop in vector_props:
            print '\t\t{}:'.format(prop), vector_props[prop]
        print '\tmaterial textureProperties:', material['textureProperties']
        print '\tmaterial keywordMap:', material['keywordMap']
        print '\tmaterial tagMap:', material['tagMap']

    # ボーンの追加パラメータ
    print 'humanoid:'
    humanoid = vrm['humanoid']
    for hum in humanoid:
        if hum == 'humanBones':
            # ボーンの対応表
            for node in sorted(humanoid[hum], key=lambda x: x['node'])[:2]:
                print '\t\t', node
        else:
            print '\t{}:'.format(hum), humanoid[hum]

    # モデル名、バージョン、権利者情報など
    print 'meta:'
    meta = vrm['meta']
    for key in meta:
        print '\t{}:'.format(key), meta[key]

    blend_groups = vrm['blendShapeMaster']['blendShapeGroups']
    print 'blendShapeMaster blendShapeGroups:'
    for key in blend_groups:
        print '\tbind group:', key['name'], key['presetName']
        print '\t\tmaterial values', key['materialValues']
        binds = key['binds']
        for bind in binds:
            # メッシュインデックス
            mesh = gltf['meshes'][bind['mesh']]
            print '\t\tmesh[{}]:'.format(bind['mesh']), mesh['name']
            targets = [primitive['targets'] for primitive in mesh['primitives'] if 'targets' in primitive][0]
            print '\t\ttargets[{}]:'.format(bind['index']), targets[bind['index']]

    # 視点位置、頭モデルの表示有無などを指定
    print 'firstPerson:'
    first_person = vrm['firstPerson']
    for eye in first_person:
        print '\t{}:'.format(eye), first_person[eye]

    return


def display_material(gltf):
    # テクスチャ、マテリアル情報表示
    materials = gltf['materials']

    images = ['{} ({})'.format(image['uri'], image['name']) for i, image in enumerate(gltf['images'])]
    textures = [images[texture['source']] for texture in gltf['textures']]

    print 'images:'
    for i, image in enumerate(images):
        print '\timage[{}]'.format(i), image

    print 'textures:'
    for i, texture in enumerate(textures):
        print '\ttexture[{}]'.format(i), texture

    print 'materials:'
    for i, material in enumerate(materials):
        print '\tmaterial[{}]:'.format(i), material['name']
        base_texture = material['pbrMetallicRoughness']['baseColorTexture']
        print '\t\tbase texture:', textures[base_texture['index']]
        if 'normalTexture' in material:
            normal_texture = material['normalTexture']
            print '\t\tnormal texture:', textures[normal_texture['index']]
        if 'emissiveTexture' in material:
            emissive_texture = material['emissiveTexture']
            print '\t\temissive texture:', textures[emissive_texture['index']]

    vrm = gltf['extensions']['VRM']
    vrm_materials = vrm['materialProperties']
    print 'vrm materials:'
    for i, material in enumerate(vrm_materials):
        # 材質のシェーダーパラメータ
        print '\tmaterial[{}]:'.format(i), material['name']
        print '\t\tshader:', material['shader']
        texture_props = material['textureProperties']
        for name in texture_props:
            print '\t\t{}:'.format(name), textures[texture_props[name]]


def display_index(gltf):
    accessors = gltf['accessors']
    buffer_views = gltf['bufferViews']

    meshes = gltf['meshes']
    for mesh in meshes:
        print mesh['name']
        primitives = mesh['primitives']
        mat_primitives = groupby(primitives, lambda x: x['material'])

        for material, primitives in mat_primitives:
            print '\tmaterial:', material
            print '\tprimitives:'
            for primitive in primitives:
                print '\t\tindices accessor:', accessors[primitive['indices']]
                indices_buffer = accessors[primitive['indices']]['bufferView']
                print '\t\tindices buffer:', buffer_views[indices_buffer]
                # print 'attributes accessor:', accessors[primitive['attributes']['POSITION']]


def stat_gltf(gltf):
    # モデル情報表示
    vrm = gltf['extensions']['VRM']
    print 'vrm materials:', len(vrm['materialProperties'])
    print 'materials:', len(gltf['materials'])
    print 'textures:', len(gltf['textures'])
    print 'images:', len(gltf['images'])

    meshes = gltf['meshes']
    print 'meshes', len(meshes)
    print 'total primitives:', sum([len(m['primitives']) for m in meshes])
    for mesh in meshes:
        print '\tprimitives:', len(mesh['primitives'])
