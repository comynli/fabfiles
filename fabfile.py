# encoding=utf-8

import os
import sys
import inspect
import pymysql
import pymysql.cursors
from fabric.api import env
from fabric.colors import red

__author__ = 'xuemingli'

DEBUG = False

if DEBUG:
    import traceback


class RoleDef(dict):
    def __init__(self, *args, **kwargs):
        self.query = 'select h.`ip` as ip, h.`port` as port, h.`user` as user ' \
                     'from groups g, hosts h ' \
                     'where g.name = "%s"  and g.id = h.group'
        self.conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="12qwaszx", db="servers",
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.conn.cursor()
        super(dict, self).__init__()

    def __getitem__(self, key):
        self.cur.execute(self.query % key)
        rows = self.cur.fetchall()
        concat = lambda x: '%s@%s:%d' % (x['user'], x['ip'], x['port'])
        ret = [concat(x) for x in rows]
        return ret

    def __contains__(self, key):
        query = "select name from groups where name='%s'" % key
        self.cur.execute(query)
        row = self.cur.fetchone()
        if row:
            return True
        return False

    def get(self, name):
        return self.__getitem__(name)


def load_module(module):
    sys.path.append("modules")
    try:
        return __import__(module)
    except Exception, e:
        print " %s: load module %s error" % (red("[ERROR]"), module)
        if DEBUG:
            print traceback.format_exc()
        sys.exit(1)


def load_modules(cf):
    for fname in os.listdir("./modules"):
        name, ext = os.path.splitext(fname)
        if ext and ext == ".py" and not name.startswith("_"):
            cf.f_locals[name] = load_module(name)


cf = inspect.currentframe()
load_modules(cf)

env.roledefs = RoleDef()
env.DEBUG = DEBUG