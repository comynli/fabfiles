# encoding=utf-8

import os
from functools import partial
from jinja2 import FileSystemLoader, Environment, TemplateNotFound, TemplateError, StrictUndefined, nodes
from fabric.api import run, sudo, prompt, task, abort, env, settings, hide
from fabric.contrib.console import confirm
from fabric.colors import green, red

__author__ = 'xuemingli'

SCRIPTS_PATH = "./scripts"
TEMP_PATH = "./tmp"
ENV = Environment(loader=FileSystemLoader(SCRIPTS_PATH), undefined=StrictUndefined)


def render(_name, **kwargs):
    try:
        t = ENV.get_template("%s.sh" % _name)
        return t.render(kwargs)
    except TemplateNotFound, e:
        abort("script '%s' not found" % _name)
    except TemplateError, e:
        abort("compile '%s' error %s" % (_name, e))


def get_scripts():
    scripts = ENV.list_templates()
    return zip(range(1, len(scripts)+1), [os.path.splitext(x)[0] for x in scripts])


def get_variables(_name):
    try:
        t = ENV.get_template("%s.sh" % _name)
        ast = ENV.parse(open(t.filename).read())
        ret = list()
        output = ast.body[0]
        for node in output.nodes:
            if isinstance(node, nodes.Filter):
                name = node.node.name
                filter = node.name
                if filter != 'default':
                    value = None
                else:
                    value = node.args[0].value
                ret.append((name, value))
            if isinstance(node, nodes.Name):
                name = node.name
                value = None
                ret.append((name, value))
        return list(set(ret))
    except TemplateNotFound, e:
        abort("script '%s' not found" % _name)
    except TemplateError, e:
        abort("compile '%s' error %s" % (_name, e))


def scripts_validate(scripts, i):
    try:
        script_id = int(i)
        script_names = [x[1] for x in scripts if x[0] == script_id]
        if len(script_names) == 1:
            return script_names[0]
        raise Exception("script %s not found" % i)
    except ValueError:
        if any([x for x in scripts if x[1] == i.strip()]):
            return i.strip()
        raise Exception("package %s not found" % i)


def notnull_validate(i):
    if i is None:
        raise Exception("input is null")
    elif isinstance(i, str) or isinstance(i, unicode):
        if i.strip() == "":
            raise Exception("input is null")
        else:
            return i.strip()
    else:
        return i


@task(name="run")
def run_script(_name, **kwargs):
    s = render(_name, **kwargs)
    if not env.DEBUG:
        with settings(hide("running")):
            run(s)
    else:
        run(s)


@task(name="sudo")
def run_script_with_sudo(_name, _user="root", **kwargs):
    s = render(_name, **kwargs)
    if not env.DEBUG:
        with settings(hide("running"), sudo_user=_user):
            sudo(s)
    else:
        with settings(sudo_user=_user):
            sudo(s)


@task(name="interactive")
def interactive(_user="root"):
    scripts = get_scripts()
    print green("scripts list:\n")
    for i, s in scripts:
        print "\t[%s]\t%s" % (green(i), s)
    _name = prompt("please select a script:", validate=partial(scripts_validate, scripts))
    kwargs = dict()
    variables = get_variables(_name)
    if len(variables) > 0:
        print red("\nsome variables need...\n")
        for key_name, default in variables:
            if default:
                kwargs[key_name] = prompt("%s:" % key_name, default=default, validate=notnull_validate)
            else:
                kwargs[key_name] = prompt("%s:" % key_name, validate=notnull_validate)

        if not confirm("you'll run %s with:\n\n\t %s \n\n are you sure? " % \
                (_name, "\n\t".join(["%s=>%s" % (k, v) for k, v in kwargs.items()]))):
            abort("user cancel")
    else:
        if not confirm("you'll run %s, are you sure? " % _name):
            abort("user cancel")
    s = render(_name, **kwargs)
    if not env.DEBUG:
        with settings(hide("running"), sudo_user=_user):
            sudo(s)
    else:
        with settings(sudo_user=_user):
            sudo(s)