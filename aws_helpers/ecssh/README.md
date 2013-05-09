ecssh: A wrapper for ssh to EC2 instances
=========================================
ssh'ing to dynamic EC2 instances which don't have meaningful DNS entries,
hostnames, or any semblance of persistence sucks.

This script tries to fix that. It uses boto to wrap the EC2 API, and caches
instances with the keypair and user name which were most recently used to
connect to it.

Installation
------------
You're on your own. setup.py to come later.

Change the DEFAULT_KEY in the header to your most commonly used keypair.

Check out the imports for dependances. e.g.,

* boto
* dateutil

... and add it to your path, or a bash alias, whatever.

Usage
-----

* `ecssh -n` access the most recently launched instance
* `ecssh foobarname` search for an instance with the Name tag == "foobarname"
* `ecssh i-f928ec22` ssh to an individual instance
* `ecssh -u user` set a user manually (defaults to 'ubuntu')
* `ecssh --help` yeah, it has help

TODO
----
* Install script
* Better error checking
* Sane settings
* non-default user/keypair aren't well tested
