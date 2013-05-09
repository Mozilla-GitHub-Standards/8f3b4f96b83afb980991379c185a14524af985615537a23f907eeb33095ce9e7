#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
. ${SCRIPT_DIR}/../build_functions.sh

PACKAGE='butter'
REPODIR='git@github.com:jdotpz/butter.git'
DEST_DIR=${PACKAGE}
HOMEPAGE='https://github.com/jdotpz/butter.git'
DESCRIPTION='(MoFo) butter nodes (node.js)'
BASE_DIR=/var/www

check_args $1 $2

cd $BASE_DIR

clone_app
cd $DEST_DIR
checkout_tag
add_appinfo
clean_git

build_node
cd $BASE_DIR
cd $DEST_DIR
node make css
build_package
#include_in_botbuilds