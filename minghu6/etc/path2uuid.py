# -*- coding:utf-8 -*-
# !/usr/bin/env python3

"""

"""
import os
import sqlite3
import uuid

from minghu6.io.stdio import askoverride
from minghu6.algs.userdict import remove_key


__all__ = ['path2uuid', 'Path2UUID']


def sqlite_escape(s):
    s = s.replace("'", "''")

    return s


def path2uuid(i, d=False, db=None, rename=True, quiet=False):
    """

    :param i: input
    :param d: flag for if the mapping direction should be reversed
    :param rename:
    :param db:
    :param quiet:
    :return: result_name in db
    """

    create_tb = ('\n'
                 '        CREATE TABLE IF NOT EXISTS Path2UUID\n'
                 '        (I VARCHAR UNIQUE,\n'
                 '         Tmp VARCHAR UNIQUE\n'
                 '        );\n'
                 )

    if db is None:
        db = '.path2uuid.sqlite3'

    conn = sqlite3.connect(db)
    conn.execute(create_tb)
    cur = conn.cursor()

    _, ext = os.path.splitext(os.path.basename(i))
    escaped_i = sqlite_escape(i)

    if not d:

        tmp_base = os.path.join(os.path.dirname(i),
                                uuid.uuid3(uuid.NAMESPACE_DNS,
                                           os.path.basename(i)).hex)

        tmp = tmp_base + ext
        try:
            insert_sql = "INSERT INTO Path2UUID VALUES ('%s', '%s')" % (escaped_i, tmp)
            try:
                cur.execute(insert_sql)
            except sqlite3.IntegrityError:
                if quiet:
                    pass
                else:
                    raise

            if rename:
                if askoverride(tmp, default=True):
                    os.remove(tmp)
                os.rename(i, tmp)
        except:
            conn.close()
            raise
        else:
            conn.commit()
            return tmp

    else:
        select_sql = """SELECT I FROM Path2UUID WHERE Tmp='%s' """ % escaped_i

        cur.execute(select_sql)
        res = cur.fetchone()
        if res is None:
            return

        res = res[0]
        try:
            output = res
            if rename:
                if askoverride(output, default=True):
                    os.remove(output)
                try:
                    os.rename(i, output)
                except:
                    if quiet:
                        pass
                    else:
                        raise

            delete_sql = """DELETE FROM Path2UUID WHERE Tmp='%s' """ % escaped_i
            cur.execute(delete_sql)
        except:
            raise
        else:
            conn.commit()
            return res
            #


class Path2UUID:

    def __init__(self, *fnlist, **other_kwargs):
        self.fnlist = fnlist
        self.path2uuid_kwargs = remove_key(other_kwargs, 'd')
        self.tmp_fnlist = []

    def __enter__(self):
        for fn in self.fnlist:
            self.tmp_fnlist.append(path2uuid(fn, **self.path2uuid_kwargs))

    def __exit__(self, exc_type, exc_val, exc_tb):
        for fn in self.tmp_fnlist:
            path2uuid(self.tmp_fnlist, d=True, **self.path2uuid_kwargs)

