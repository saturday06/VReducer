#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser
from os import mkdir
from os.path import dirname, join, exists, basename

from vrm.debug import stat_gltf
from vrm.vrm import load
from vrm.reducer import reduce_vroid


def main(argv):
    parser = ArgumentParser()
    parser.add_argument('path', help=u'VRM file exported by VRoid Studio.')
    parser.add_argument('-f', '--force', action='store_true', help=u'Overwrite file if already exists same file.')
    opt = parser.parse_args(argv)

    path = opt.path
    print path

    # vrm読み込み
    vrm = load(path)

    stat_gltf(vrm.gltf)

    print '-' * 30
    vrm.gltf = reduce_vroid(vrm.gltf)

    print '-' * 30
    stat_gltf(vrm.gltf)

    save_dir = join(dirname(path), 'result')
    if not exists(save_dir):
        mkdir(save_dir) # 出力先作成

    save_path = join(save_dir, basename(path))
    # 上書き確認
    if not opt.force and exists(save_path) and raw_input('Already exists file. Overwrite?(y/N):').lower not in ['y', 'yes']:
        return

    # vrm保存
    vrm.save(save_path)


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding(sys.getfilesystemencoding())

    main(sys.argv[1:])
