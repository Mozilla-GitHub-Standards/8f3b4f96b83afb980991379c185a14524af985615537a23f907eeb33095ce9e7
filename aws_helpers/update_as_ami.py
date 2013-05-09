#!/usr/bin/env python

import argparse
import boto
import time

def main():
    parser = argparse.ArgumentParser(description='Update the launch config for an autoscale group to use a new AMI')
    parser.add_argument('template_instance', action='store')
    parser.add_argument('autoscale_group', action='store')
    parser.add_argument('new_lc_name', action='store')
    args = parser.parse_args()
    ec2conn = boto.connect_ec2()
    image_id = ec2conn.create_image(args.template_instance, args.new_lc_name)
    time.sleep(3)
    image = ec2conn.get_all_images([image_id])[0]
    print "Creating AMI: " + image_id
    while (image.state != 'available'):
        time.sleep(3)
        image = ec2conn.get_all_images([image_id])[0]
    print "Done"
    asconn = boto.connect_autoscale()
    group = asconn.get_all_groups([args.autoscale_group], 1)[0]
    old_lc_name = group.launch_config_name
    print 'Old launch configuration: ' + old_lc_name
    launch_config = asconn.get_all_launch_configurations(names=[old_lc_name],
                                                                max_records=1)[0]
    print 'Old AMI: ' + launch_config.image_id
    launch_config.name = args.new_lc_name
    launch_config.image_id = image_id
    print 'Creating launch configuration: ' + args.new_lc_name
    asconn.create_launch_configuration(launch_config)
    print 'Updating autoscale group with new launch configuration'
    group.launch_config_name = launch_config.name
    # ugh fix this.
    # currently, boto does not get the group's max size. fill it in manually.
    # will be fixed in 2.6.0 or further patches to 2.5.
    group.max_size = 100
    group.update()
    print 'Group ' + group.name + ' configured to use launch configuration ' + launch_config.name + ' with AMI ' + launch_config.image_id

if __name__ == '__main__':
    main()