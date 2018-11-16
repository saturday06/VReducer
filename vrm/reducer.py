#!/usr/bin/env python
# -*- coding:utf-8 -*-
import struct
from copy import deepcopy
from io import BytesIO

from PIL import Image

from cleaner import clean

"""
VRoidモデルの削減処理
"""


def find_mesh(gltf, name):
    meshes = gltf['meshes']
    return [mesh for mesh in meshes if mesh['name'] == name][0]


def isolated_primitives(gltf, name):
    """
    髪プリミティブ統合
    ※連続したプリミティブであることを前提
    """
    gltf = deepcopy(gltf)
    # ヘアメッシュ
    hair_mesh = find_mesh(gltf, name)

    # ヘアメッシュ内のプリミティブインデックスのアクセッサーを列挙
    hair_primitive_indices = [primitive['indices'] for primitive in hair_mesh['primitives']]

    # バッファービューを列挙
    buffer_views = map(lambda indices: indices['bufferView'], hair_primitive_indices)
    head_view = buffer_views[0]
    # 統合したバッファービューを作成
    buffer = head_view['buffer']
    offset = head_view['byteOffset']
    data = b''.join(map(lambda view: view['data'], buffer_views))  # バイトデータ
    new_view = {
        'buffer': buffer,
        'byteOffset': offset,
        'byteLength': len(data),
        'target': head_view['target'],
        'data': data
    }
    # NOTE; VRoidでは出力されない
    if 'byteStride' in head_view:
        new_view['byteStride'] = head_view['byteStride']
    gltf['bufferViews'].append(new_view)

    # アクセッサーを統合
    accessor_count = sum(map(lambda x: x['count'], hair_primitive_indices))  # アクセッサー総要素数
    head_indices = hair_primitive_indices[0]
    new_accessor = {
        'count': accessor_count,
        'byteOffset': head_indices['byteOffset'],
        'bufferView': new_view,
        'componentType': head_indices['componentType'],
        'type': head_indices['type'],
        'normalized': head_indices['normalized']
    }
    gltf['accessors'].append(new_accessor)

    # 髪メッシュのプリミティブを統合
    hair_primitives = hair_mesh['primitives']
    hair_primitive_head = hair_primitives[0]
    new_hair_primitive = {
        'mode': hair_primitive_head['mode'],
        'indices': new_accessor,
        'attributes': hair_primitive_head['attributes'],
        'material': hair_primitive_head['material']
    }
    hair_mesh['primitives'] = [new_hair_primitive]

    return gltf


def remove_primitives(gltf, material_names):
    """
    指定したマテリアル名のプリミティブを削除する
    """
    gltf = deepcopy(gltf)
    # プリミティブ削除
    for mesh in gltf['meshes']:
        mesh['primitives'] = filter(lambda p: p['material']['name'] not in material_names, mesh['primitives'])
    return gltf


def shrink_material(gltf):
    # VRMからバンプマップ、スフィアマップを削除
    gltf = deepcopy(gltf)

    for material in gltf['materials']:
        for tex_name in ['emissiveTexture', 'normalTexture', 'emissiveTexture']:
            if tex_name in material:
                del material[tex_name]

    vrm_materials = gltf['extensions']['VRM']['materialProperties']
    for material in vrm_materials:
        # バンプマップ、スフィアマップ削除
        unused = ['_BumpMap', '_SphereAdd']
        material['textureProperties'] = {k: v for k, v in material['textureProperties'].items() if k not in unused}

        # 法線マップ、リムライティング無効化
        remove_options = ['_NORMALMAP', 'MTOON_OUTLINE_COLOR_FIXED']
        material['keywordMap'] = {k: v for k, v in material['keywordMap'].items() if k not in remove_options}

    return gltf


def find_material(gltf, name):
    for material in gltf['materials']:
        if name in material['name']:
            return material
    return None


def find_vrm_material(gltf, name):
    for material in gltf['extensions']['VRM']['materialProperties']:
        if name in material['name']:
            return material
    return None


def primitives_by_material(gltf, material_name):
    for mesh in gltf['meshes']:
        for primitive in mesh['primitives']:
            if material_name in primitive['material']['name']:
                yield primitive


def load_img(image):
    # 画像データをPILで読み込む
    buffer_view = image['bufferView']
    return Image.open(BytesIO(buffer_view['data']))


def image2bytes(img, fmt):
    # PILの画像データを指定フォーマットの画像ファイルデータに変換する
    with BytesIO() as bio:
        img.save(bio, format=fmt)
        return bio.getvalue()


def max_size(resize_info):
    # リサイズ情報から最大幅を計算する
    max_w, max_h = 0, 0
    for name, info in resize_info.items():
        pos = info['pos']
        size = info['size']
        max_w = max(max_w, pos[0] + size[0])
        max_h = max(max_h, pos[1] + size[1])
    return max_w, max_h


def combine_material(gltf, resize_info, base_material_name):
    # 制服、スカート、リボン、靴マテリアル結合
    gltf = deepcopy(gltf)
    max_w, max_h = max_size(resize_info)

    # 配置
    one_image = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
    for name, info in resize_info.items():
        material = find_vrm_material(gltf, name)
        if not material:
            raise Exception('material {} not found.'.format(name))
        texture = material['textureProperties']['_MainTex']
        source = texture['source']
        image = load_img(source)
        one_image.paste(image.resize(info['size'], Image.LANCZOS), info['pos'])
    width, height = map(float, one_image.size)
    new_view = {'data': image2bytes(one_image, 'png')}
    new_image = {'mimeType': 'image/png', 'bufferView': new_view}
    # one_image.show()

    # テクスチャ更新
    vrm_material = find_vrm_material(gltf, base_material_name)
    texture = vrm_material['textureProperties']['_MainTex']
    texture['source'] = new_image
    gltf['images'].append(new_image)
    gltf['bufferViews'].append(new_view)

    # マテリアル統一(テクスチャを更新しているので適用するだけで良い)
    material = find_material(gltf, base_material_name)

    # マテリアル名、プリミティブ、bufferViewインデックス
    def list_primitives():
        for name in resize_info:
            for primitive in primitives_by_material(gltf, name):
                view_index = gltf['bufferViews'].index(primitive['attributes']['TEXCOORD_0']['bufferView'])
                yield (name, primitive, view_index)

    def uv_scale(name):
        # スケール率計算
        paste_info = resize_info[name]
        paste_pos = paste_info['pos']
        paste_size = paste_info['size']
        x, y = (paste_pos[0] / width, paste_pos[1] / height)
        w, h = (paste_size[0] / width, paste_size[1] / height)
        return x, y, w, h

    # オリジナルバッファー
    original_view_datas = {}
    for _, _, view_index in list_primitives():
        if view_index not in original_view_datas:
            original_view_datas[view_index] = deepcopy(gltf['bufferViews'][view_index]['data'])

    for name, primitive, view_index in list_primitives():
        # マテリアル更新
        primitive['material'] = material
        # 頂点インデックス一覧
        accessor = primitive['indices']
        indices_buffer = accessor['bufferView']['data']
        indices_offset = accessor['byteOffset']
        indices = map(lambda i: struct.unpack_from('I', indices_buffer, indices_offset + i * 4)[0],
                      xrange(accessor['count']))

        # uvバッファ
        original_data = original_view_datas[view_index]
        uv_accessor = primitive['attributes']['TEXCOORD_0']
        uv_view = uv_accessor['bufferView']
        uv_data = uv_view['data']

        # スケール率計算
        x, y, w, h = uv_scale(name)
        for index in set(indices):
            uv_offset = index * 8
            ou, ov = struct.unpack_from('2f', original_data, uv_offset)
            u, v = struct.unpack_from('2f', uv_data, uv_offset)
            if ou != u or ov != v:
                continue  # 更新されていればスキップ
            u, v = (x + u * w, y + v * h)
            uv_data = uv_data[:uv_offset] + struct.pack('2f', u, v) + uv_data[uv_offset + 8:]
        uv_view['data'] = uv_data  # 更新
    return gltf


def eye_extra_name(gltf):
    # 特殊目><のマテリアル名
    if find_material(gltf, '_EyeExtra_'):
        return '_EyeExtra_'
    # v0.2.15：F00_000_EyeExtra_01_EYE -> v0.3.0：F00_000_FaceEyeSP_00_EYE
    return '_FaceEyeSP_'


# VROID服装種別
CLOTH_NAKED = 'BIG_BOSS'
CLOTH_STUDENT = 'STUDENT'
CLOTH_ONE_PIECE = 'ONE_PIECE'


def get_cloth_type(gltf):
    # 服装判定
    names = map(lambda x: x['name'], gltf['materials'])
    for name in names:
        if name.startswith('F00_001'):
            return CLOTH_STUDENT
        if name.startswith('F00_002'):
            return CLOTH_ONE_PIECE
    return CLOTH_NAKED


def reduce_vroid(gltf):
    # VRoidモデルの軽量化

    # 髪プリミティブ統合
    print 'combining hair primitives...'
    gltf = isolated_primitives(gltf, 'Hair001.baked')

    # バンプマップ、スフィアマップを削除
    print 'shrinking materials...'
    gltf = shrink_material(gltf)

    # マテリアルを結合
    print 'combining materials...'

    cloth_type = get_cloth_type(gltf)

    if cloth_type == CLOTH_STUDENT:
        # 制服上下、リボン、靴
        gltf = combine_material(gltf, {
            '_Tops_': {'pos': (0, 0), 'size': (2048, 1536)},
            '_Bottoms_': {'pos': (0, 1536), 'size': (512, 512)},
            '_Accessory_': {'pos': (512, 1536), 'size': (512, 512)},
            '_Shoes_': {'pos': (1024, 1536), 'size': (512, 512)}
        }, '_Tops_')

    # ボディ、顔、白目、口
    gltf = combine_material(gltf, {
        '_Body_': {'pos': (0, 0), 'size': (1536, 2048)},
        '_Face_': {'pos': (1536, 0), 'size': (512, 512)},
        '_EyeWhite_': {'pos': (1536, 512), 'size': (512, 512)},
        '_FaceMouth_': {'pos': (1536, 1024), 'size': (512, 512)},
    }, '_Face_')

    # アイライン、まつ毛
    gltf = combine_material(gltf, {
        eye_extra_name(gltf): {'pos': (0, 0), 'size': (1024, 512)},
        '_FaceEyeline_': {'pos': (0, 512), 'size': (1024, 512)},
        '_FaceEyelash_': {'pos': (0, 1024), 'size': (1024, 512)}
    }, '_FaceEyeline_')

    # 瞳孔、ハイライト
    gltf = combine_material(gltf, {
        '_EyeIris_': {'pos': (0, 0), 'size': (1024, 512)},
        '_EyeHighlight_': {'pos': (0, 512), 'size': (1024, 512)}
    }, '_EyeIris_')

    # 髪の毛、頭の下毛
    gltf = combine_material(gltf, {
        '_HairBack_': {'pos': (0, 0), 'size': (1024, 1024)},
        '_Hair_': {'pos': (1024, 0), 'size': (512, 1024)}
    }, '_Hair_')

    # 不要要素削除
    print 'cleaning...'
    return clean(gltf)
