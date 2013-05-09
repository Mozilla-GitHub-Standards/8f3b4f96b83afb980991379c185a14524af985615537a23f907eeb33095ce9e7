#!/usr/bin/env python

import boto

ec2 = boto.connect_ec2()

def get_instance(instance_id):
    reservation = ec2.get_all_instances([instance_id])
    result = [i for i in reservation.instances if i.id == instance_id]
    if len(result) == 1:
        return result
    raise ValueError('Instance %s not found' % instance_id)

def _get_instances(instance_ids):
    """ given a list of instance IDs, return the boto instance objects """
    instances = []
    reservations = ec2.get_all_instances(instance_ids)
    for r in reservations:
        for i in r.instances:
            instances.append(i)
    if instances:
        return instances
    raise ValueError('No instances found in list')

def _get_autoscale_group(name):
    conn = boto.connect_autoscale()
    groups = conn.get_all_groups(names=[name])

    if len(groups) == 1:
        return groups[0]
    raise ValueError('Autoscale group %s not found' % name)

def get_as_instances(name):
    # TODO: filter on instance health
    group = _get_autoscale_group(name)

    as_instance_ids = [i.instance_id for i in group.instances]
    return _get_instances(as_instance_ids)


# TODO: this needs to be moved to facade with other hostname accessors
def from_as_group(name):
    instances = get_as_instances(name)
    if instances:
        hosts = [i.dns_name for i in instances]
    else:
        hosts = None
    return hosts

def main():
    instances = get_as_instances('openbadges-production-as')

    for i in instances:
        print i.dns_name

if __name__ == '__main__':
    main()
