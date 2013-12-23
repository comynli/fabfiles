# encoding=utf-8

import os
from functools import partial
from fabric.api import run, put, task, prompt, abort
from fabric.contrib.files import exists
from fabric.contrib.console import confirm

__author__ = 'xuemingli'


PACKAGE_PATH = "./package"
DEPLOY_PATH = "/data/webapps"


class NoPackageFoundException(Exception):
    pass


def list_local_packages(num=5):
    num = int(num)
    packages = os.listdir(PACKAGE_PATH)
    return zip(range(1, num+1), packages[:num])


def print_packages(packages):
    for pkg in packages:
        print "%d\t%s" % pkg


def package_validate(packages, i):
    try:
        pkg_id = int(i)
        pkgs = [x[1] for x in packages if x[0] == pkg_id]
        if len(pkgs) == 1:
            pkg = os.path.join(PACKAGE_PATH, pkgs[0])
            if os.path.isfile(pkg):
                return pkg
        raise NoPackageFoundException("package %s not found" % i)
    except ValueError:
        if any([x for x in packages if x[1] == i.strip()]):
            pkg = os.path.join(PACKAGE_PATH, i.strip())
            if os.path.isfile(pkg):
                return pkg
        raise NoPackageFoundException("package %s not found" % i)


@task
def deploy(num=5, deploy_path=None):
    packages = list_local_packages(num)
    print_packages(packages)
    pkg = prompt("please select a package", default=1, validate=partial(package_validate, packages))
    if not deploy_path:
        deploy_path = DEPLOY_PATH
    if not confirm("you'll deploy %s to %s, are you sure" % (pkg, deploy_path)):
        abort("user cancel")
    if not exists(deploy_path):
        run("mkdir -p" % deploy_path)
    put(pkg, deploy_path)
    #TODO your deploy scripts
