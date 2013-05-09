#!/usr/bin/env python

import pickle
import os
import sys
import re
import subprocess
from itertools import ifilter
from optparse import OptionParser
from dateutil import parser
import boto.ec2

CACHE_FILE='~/.essh-cache'
DEFAULT_KEY='~/.ec2/FILLMEOUT.pem'

class InstanceCache(object):
    """ Save user/keypair, and attempt to use it for future connections"""
    def __init__(self):
        self._instances = []
        self._cache_file = os.path.expanduser(CACHE_FILE)
        if os.path.isfile(self._cache_file):
            self._load()
    def _load(self):
        fh = open(self._cache_file, "r+")
        try:
            p = pickle.load(fh)
            if p:
                self._instances = p
        except EOFError:
            pass
        fh.close()
    def add(self, instance_id, key, user):
        existing = self.get(instance_id)
        if existing:
            print "... replacing previous cached entry"
            self._instances.remove(existing)
        i = {}
        i['id'] = instance_id
        i['key'] = key
        i['user'] = user
        self._instances.append(i)
    def get(self, instance_id):
        result = [i for i in self._instances if i['id'] == instance_id]
        if result:
            return result[0]
    def save(self):
        fh = open(self._cache_file, "w")
        pickle.dump(self._instances, fh, 2)
        fh.close()

def get_instances():
    instances = []
    reservations = conn.get_all_instances()
    for r in reservations:
        for i in r.instances:
            instances.append(i)
    return set(instances)

def find_instance_id(instance_id, instances):
    result = [i for i in instances if i.id == instance_id]
    if result:
        return result[0]
    else:
        return False

def find_by_tag(value, tag):
    result = [i for i in instances if i.tags.get(tag, '') == value]
    return result

def iso_to_epoch(iso):
    """Convert an ISO time string into an epoch timestamp"""
    dt = parser.parse(iso)
    return dt.strftime("%s")

def find_newest(instances):
    instances_descending =  sorted(instances, key=lambda i:
                                   iso_to_epoch(i.launch_time), reverse=True)
    return instances_descending[0]

def connect(instance, key=DEFAULT_KEY, user='ubuntu'):
    # TODO: ensure that key exists
    #       if connection succeeds, cache the entry
    key_path = os.path.expanduser(key)
    cmd = ['ssh', '-i', key_path, '%s@%s' % (user, instance.dns_name)]
    print "Connecting to %s (%s) - %s@%s" % (instance.tags.get('Name', ''),
                                          instance.id, user, instance.dns_name)
    try:
        status = subprocess.call(cmd, shell=False)
    except KeyboardInterrupt:
        pass
    if status == 0: # ssh was successful
        return True
    else:
        return False

def is_instance(arg):
    pattern = re.compile(r'i-\w{8}')
    if pattern.search(arg):
        return True

optparser = OptionParser(usage="%prog [options] INSTANCE")
optparser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                     default=False, help="print verbose output")
optparser.add_option("-u", "--user", dest="user", default='ubuntu',
                     help="(optional) specify a user other than 'ubuntu'")
optparser.add_option("-i", "--identity", dest="key",
                     help="connect using this keypair")
optparser.add_option("-n", "--newest", action="store_true", dest="connect_newest",
                  default=False, help="connect to the newest instance")
optparser.add_option("-w", action="store_true", dest="west",
                  default=False, help="connect to the west region")
(options, args) = optparser.parse_args()

if args:
    search_term = args[0]
else:
    search_term = False

if __name__ == '__main__':

    if options.west:
        conn = boto.ec2.connect_to_region('us-west-2')
    else:
        conn = boto.ec2.connect_to_region('us-east-1')

    cache = InstanceCache()
    instances = get_instances()

    if search_term:
        if is_instance(search_term):
            instance = find_instance_id(search_term, instances)
        else:
            results = find_by_tag(search_term, 'Name')
            if results:
                instance = results[0]
            else:
                sys.exit("%s: Name or instance id not found" % search_term)
    elif options.connect_newest:
        instance = find_newest(instances)
    else:
        optparser.error("Nothing to do.")

    saved = cache.get(instance.id)

    if options.key:
        DEFAULT_KEY=options.key

    if saved:
        if connect(instance, saved['key'], saved['user']): #FIXME, ugly
            cache.add(instance.id, saved['key'], saved['user'])
    else:
        print "user name / keypair unknown: guessing"
        # TODO: can't tell what credentials connect() used
        if connect(instance, user=options.user, key=DEFAULT_KEY):
            cache.add(instance.id, DEFAULT_KEY, options.user)

    cache.save()
