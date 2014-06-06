# encoding=utf-8

import os
from fabric.api import run, put, task, abort, get, env, local
from fabric.contrib.files import exists

__author__ = 'xuemingli'

KEYFILE = "./data/keymanage/id_dsa_2048_a_31.pub"


def get_ssh_type():
    out = run("ssh -V", quiet=True)
    if "openssh" in out.lower():
        return "openssh"
    return "ssh2"


def add_ssh2(key_name):
    if not exists("/root/.ssh2"):
        run("mkdir /root/.ssh2")
    run("/bin/cp -f /tmp/%s /root/.ssh2")
    run("touch /root/.ssh2/authorization")
    os.makedirs("/tmp/%s" % env.host)
    get("/root/.ssh2/authorization", "/tmp/%s" % env.host)
    with open("/tmp/%s/authorization" % env.host) as f:
        for line in f:
            if "Key %s" % key_name in line:
                run("echo 'key ok'")
                local("rm -rf /tmp/%s" % env.host)
                return
    run("echo 'Key %s' >> /root/.ssh2/authorization" % key_name)


def add_openssh(key_name):
    if not exists("/root/.ssh"):
        run("mkdir -p /root/.ssh")
        run("chmod 700 /root/.ssh")
    run("ssh-keygen -f /tmp/%s -i >>/root/.ssh/authorized_keys" % key_name)
    run("chmod 644 /root/.ssh/authorized_keys")
    run("rm -rf /tmp/%s" % key_name)


@task
def add(key=KEYFILE):
    ssh_type = get_ssh_type()
    if not os.path.isfile(key):
        abort("key file not is file")
    key_name = os.path.basename(key)
    put(key, "/tmp/%s" % key_name)
    if ssh_type == "openssh":
        add_openssh(key_name)
    else:
        add_ssh2(key_name)

