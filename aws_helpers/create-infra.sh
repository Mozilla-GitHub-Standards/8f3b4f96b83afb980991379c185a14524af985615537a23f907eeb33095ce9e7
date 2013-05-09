#!/bin/bash

set -e # bail on any failures

# Available certs
#CERT="arn:aws:iam::acct#:server-certificate/certname"


# Fill this out
AS="openbadger-wm-production-as"
LC="openbadger-wm-production-64"
ELB="openbadger-wm-production"
AMI="ami-3fec7956"
#AMI="ami-43e2772a"
SG="openbadger-ec2-sg"
SIZE="m1.small"
CONFIG="/u/mozilla/cloud-init/openbadger-wm-production-64"
AS_SCALEUP_POLICY_NAME="${ELB}-scaleup"
AS_SCALEDOWN_POLICY_NAME="${ELB}-scaledown"
HIGHCPU_ALARM_NAME="${ELB}-HighCPU"
LOWCPU_ALARM_NAME="${ELB}-LowCPU"
HIGHCPU_THRESHOLD="50"
LOWCPU_THRESHOLD="10"
HEALTHCHECK_TIMEOUT="10"
HEALTHCHECK_INTERVAL="15"
UNHEALTHY_THRESHOLD="2"
HEALTHY_THRESHOLD="2"
CREATE_ELB="1" #If you already have an ELB, set to 0.  If not, set to 1 to create.
APP="openbadger-wm"
APPENV="production"



##############################
## ELB CREATION
if [[ $CREATE_ELB -eq 1 ]]
    then
    # CREATE ELB
    elb-create-lb ${ELB} --listener "protocol=HTTP, lb-port=80, instance-port=80" \
                     --availability-zones us-east-1b,us-east-1c,us-east-1d
    fi

# Update/Change listeners
# delete listener first (doesn't remove the LB), then recreate
#elb-delete-lb-listeners ${ELB} --lb-ports 80
#elb-delete-lb-listeners ${ELB} --lb-ports 443
#elb-create-lb-listeners ${ELB} --listener "protocol=HTTP, lb-port=80, instance-port=8080"

# This listener is for non-PCI ELB's
#elb-create-lb-listeners ${ELB} --listener "protocol=HTTPS, lb-port=443, instance-port=80, cert-id=${CERT}"

# This listener is for PCI ELB's.
#elb-create-lb-listeners ${ELB} --listener "protocol=HTTPS, lb-port=443, instance-port=443, cert-id=${CERT}"
#elb-set-lb-policies-of-listener ${ELB} --lb-port 443 --policy-names ELBDefaultNegotiationPolicy,AWSConsolePolicy-2


elb-describe-lbs ${ELB} --show-long --headers

## DONE WITH ELB CREATE
###############################


##############################
## LAUNCH CONFIG CREATION
as-create-launch-config ${LC} --key openbadger-wm --image-id ${AMI} --instance-type ${SIZE} \
        --user-data-file ${CONFIG} --group ${SG}

##############################
## AUTOSCALE GROUP CREATION
as-create-auto-scaling-group ${AS} --launch-configuration ${LC} --load-balancers \
        ${ELB} --availability-zones us-east-1b,us-east-1c,us-east-1d --min-size 0 --max-size 0 \
        --health-check-type EC2 --default-cooldown 300 --grace-period 0 \
        --tag "k=env,v=${APPENV},p=true" --tag "k=app,v=${APP},p=true"

as-update-auto-scaling-group ${AS} --max-size 10 --min-size 1 --desired-capacity 0

elb-configure-healthcheck ${ELB} --headers --target "HTTP:80/health_check?elb=true" --interval ${HEALTHCHECK_INTERVAL} --timeout ${HEALTHCHECK_TIMEOUT} --unhealthy-threshold ${UNHEALTHY_THRESHOLD} --healthy-threshold ${HEALTHY_THRESHOLD}

SCALE_UP_POLICY=`as-put-scaling-policy ${AS_SCALEUP_POLICY_NAME} --auto-scaling-group ${AS} --adjustment=4 --type ChangeInCapacity --cooldown 300`
SCALE_DOWN_POLICY=`as-put-scaling-policy ${AS_SCALEDOWN_POLICY_NAME} --auto-scaling-group ${AS} --adjustment=-2 --type ChangeInCapacity --cooldown 300`

mon-put-metric-alarm ${HIGHCPU_ALARM_NAME} --comparison-operator GreaterThanThreshold --evaluation-periods 1 --metric-name CPUUtilization --namespace "AWS/EC2" --period 600 --statistic Average --threshold ${HIGHCPU_THRESHOLD} --alarm-actions ${SCALE_UP_POLICY} --dimensions "AutoScalingGroupName=${AS}"

mon-put-metric-alarm ${LOWCPU_ALARM_NAME} --comparison-operator LessThanThreshold --evaluation-periods 1 --metric-name CPUUtilization --namespace "AWS/EC2" --period 600 --statistic Average --threshold ${LOWCPU_THRESHOLD} --alarm-actions ${SCALE_DOWN_POLICY} --dimensions "AutoScalingGroupName=${AS}"

as-put-notification-configuration ${AS} --topic-arn arn:aws:sns:us-east-1:ACCOUNTID:ec2-autoscaling --notification-types autoscaling:EC2_INSTANCE_LAUNCH,autoscaling:EC2_INSTANCE_LAUNCH_ERROR,autoscaling:EC2_INSTANCE_TERMINATE,autoscaling:EC2_INSTANCE_TERMINATE_ERROR
