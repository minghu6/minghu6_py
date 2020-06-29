# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""

"""
import datetime

__all__ = ['datetime_fromstr']


def datetime_fromstr(s, sep='-', sep_date_time=' '):
    """
    input format datetime str as follow
    2017-01-02 22:12:53
    2017-01-02 22:12
    2017-01-02
    """
    all_kind_format = ['%Y{0}%m{0}%d'.format(sep),
                       '%Y-%m-%d{0}%H:%M'.format(sep_date_time),
                       '%Y-%m-%d{0}%H:%M:%S'.format(sep_date_time),
                       '%Y-%m-%d{0}%H:%M:%S.%f'.format(sep_date_time)]

    for one_format in all_kind_format:
        try:
            d = datetime.datetime.strptime(s, one_format)
        except ValueError:
            pass
        else:
            return d

    raise ValueError('Invalid datetime str format')
