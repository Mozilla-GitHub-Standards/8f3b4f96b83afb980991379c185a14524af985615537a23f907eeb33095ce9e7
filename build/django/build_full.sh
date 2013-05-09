#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
. ${SCRIPT_DIR}/../functions.sh

PACKAGE='exampledjangoapp'
REPODIR='git@github.com:mozilla/some_repo.git'
DEST_DIR=$PACKAGE
HOMEPAGE=''
DESCRIPTION='Mozilla app (Django)'
REQUIREMENTS='requirements.txt'
BASE_DIR=/var/www

check_args $1 $2

cd $BASE_DIR

clone_app
cd $DEST_DIR
checkout_tag
add_appinfo
clean_git

build_python

build_package
include_in_botbuilds
