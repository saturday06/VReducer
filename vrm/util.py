#!/usr/bin/env python
# -*- coding:utf-8 -*-


def unique(seq):
    """
    :param seq: リスト
    :return: 重複のないリストを返す
    """
    new_list = []
    for x in seq:
        if x not in new_list:
            new_list.append(x)
    return new_list


def find(func, seq):
    """
    :param func: 条件
    :param seq: リスト
    :return: 条件を満たす最初の要素を返す、見つからなければNone
    """
    for x in seq:
        if func(x):
            return x
    return None
