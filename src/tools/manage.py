#!/usr/bin/env python2
from os.path import dirname, abspath
import os
import sys
import platform
import re

sys.path.insert(0, dirname(dirname(abspath(__file__))))


def dockerized():
    try:
        if 'docker' in open('/proc/1/cgroup').read():
            return True
    except IOError:
        return False


def getowndockerid():
    dockerid = ""
    try:
        for line in open('/proc/1/cgroup'):
            if "docker" in line:
                dockerid = re.search(r".*/docker/(.*)$", line)
                return dockerid.group(1)
    except IOError:
        return False

    if dockerid == "":
        return False


if __name__ == "__main__":
    host_name = platform.node()

    if dockerized():
        print "We are running in a docker container, using localsettings"
        config_file = "conf.localsettings"

    elif host_name:
        if '.' in host_name:
            new_host_name = host_name.replace('.', '-')
            print "Host name {0} contains dots (.) replacing by (-) and looking for conf.{1}-localsettings".format(
                host_name, new_host_name)
            host_name = new_host_name

        config_file = "conf.{}-localsettings".format(host_name)

    else:
        print "Host name is not set using default config conf.localsettings !"
        config_file = "conf.localsettings"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", config_file)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)