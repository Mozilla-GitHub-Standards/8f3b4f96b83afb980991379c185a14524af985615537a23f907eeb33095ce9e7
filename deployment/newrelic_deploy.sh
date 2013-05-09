#!/bin/bash

# Program: newrelic_deploy.sh
# Purpose: Publish a deployment notification to New Relic
# Usage: newrelic_deploy.sh "app name - env" "Short description" "Version #"

# Add the variable NEWRELIC_USER to your local profile to get credit for your
# deploys
NEWRELIC_USER="jp"

REQUIREDARGS=3
APPNAME="${1}"
DESCRIPTION="${2}"
REVISION="${3}"


usage() {
    echo "newrelic_deploy.sh usage"
    echo " ----------------------- "
    echo "newrelic_deploy.sh \"Appname - Environment\" \"Description\" \"Version Number\" "
    echo " "
    exit 0
    }


if [[ ${#} -ne $REQUIREDARGS ]]; then
    usage
fi


curl -H "x-api-key:addnewrelicapikey" -d "deployment[user]=${NEWRELIC_USER}"  -d "deployment[app_name]=$APPNAME" -d "deployment[description]=$DESCRIPTION"  -d "deployment[revision]=$REVISION" https://rpm.newrelic.com/deployments.xml
