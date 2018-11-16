#!/usr/bin/env python
# -*- coding:utf-8 -*-


def unique(seq):
    # ユニークリストを生成する
    new_list = []
    for x in seq:
        if x not in new_list:
            new_list.append(x)
    return new_list
