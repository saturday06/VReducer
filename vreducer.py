#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser
from os import mkdir
from os.path import dirname, join, exists, basename

from vrm.debug import print_stat
from vrm.reducer import reduce_vroid
from vrm.vrm import load


def parse_texture_size(texture_size_option):
    # テクスチャサイズオプションのパース
    option = texture_size_option.split(',')[:2]
    w, h = (option * 2)[:2]
    return int(w), int(h)


def main(argv):
    from vrm.version import app_name
    parser = ArgumentParser()
    parser.add_argument('path', help=u'VRM file exported by VRoid Studio.')
    parser.add_argument('-s', '--replace-shade-color', action='store_true', help=u'Replace shade color to main color.')
    parser.add_argument('-t', '--texture-size', default='2048,2048',
                        help=u'Change texture size less equal than this size. (-t 512,512)')
    parser.add_argument('-f', '--force', action='store_true', help=u'Overwrite file if already exists same file.')
    parser.add_argument('-V', '--version', action='version', version=app_name())
    opt = parser.parse_args(argv)

    path = opt.path
    print path

    # vrm読み込み
    vrm = load(path)

    print_stat(vrm.gltf)

    print '-' * 30
    vrm.gltf = reduce_vroid(vrm.gltf, opt.replace_shade_color, parse_texture_size(opt.texture_size))

    print '-' * 30
    print_stat(vrm.gltf)

    save_dir = join(dirname(path), 'result')
    if not exists(save_dir):
        mkdir(save_dir)  # 出力先作成

    save_path = join(save_dir, basename(path))
    # 上書き確認
    if not opt.force and exists(save_path):
        if raw_input('Already exists file. Overwrite?(y/N):').lower() not in ['y', 'yes']:
            return

    # vrm保存
    vrm.save(save_path)
    print 'saved.'


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding(sys.getfilesystemencoding())

    main(sys.argv[1:])
