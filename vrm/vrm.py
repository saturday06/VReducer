#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import struct

from gltf import instancing, indexing


def read_binary(path):
    with open(path, 'rb') as fi:
        return fi.read()


GLTF_MAGIC = 0x46546c67  # glTF
JSON_TYPE = 0x4e4f534a  # JSON
CHUNK_TYPE = 0x4e4942  # BIN


class VRM(object):
    def __init__(self, version, gltf, chunks):
        """
        VRMオブジェクト(VRMはglb互換)
        :param version: VRFMバージョン
        :param gltf: VRMのJSONデータ
        :param chunks: VRMのバッファデータ
        """
        self.version = version
        self.gltf = instancing(gltf, chunks)

    def save(self, path):
        """
        VRMファイル保存
        :param path: 保存先ファイルパス
        """
        with open(path, 'wb') as fo:
            # GLTF_HEADER
            gltf, chunks = indexing(self.gltf)
            gltf_encoded = json.dumps(gltf).encode('utf-8')
            glb_length = 20 + len(gltf_encoded) + sum(map(len, chunks))

            for v in [GLTF_MAGIC, self.version, glb_length, len(gltf_encoded), JSON_TYPE]:
                fo.write(struct.pack('I', v))
            fo.write(gltf_encoded)
            for chunk in chunks:
                for v in [len(chunk), CHUNK_TYPE]:
                    fo.write(struct.pack('I', v))
                fo.write(chunk)


def load(path):
    """
    VRM読み込み
    :param path: VRMファイルパス
    :return: VRMオブジェクト
    """
    glb_bin = read_binary(path)
    struct.unpack_from("II", glb_bin)

    gltf_magic, version, length = struct.unpack_from("III", glb_bin)
    assert gltf_magic == GLTF_MAGIC

    json_length, json_type = struct.unpack_from("II", glb_bin, offset=12)
    assert json_type == JSON_TYPE
    json_text = glb_bin[20:][:json_length].decode('utf-8')
    gltf = json.loads(json_text)

    offset = 20 + json_length
    chunks = []
    while offset < length:
        chunk_length, chunk_type = struct.unpack_from("II", glb_bin, offset=offset)
        assert chunk_type == CHUNK_TYPE
        chunk = glb_bin[offset + 8:][:chunk_length]
        chunks.append(chunk)
        offset += 8 + chunk_length

    return VRM(version, gltf, chunks)
