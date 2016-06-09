#!/usr/bin/env bash

die() { status=$1; shift; echo "FATAL: $*"; exit $status; }
EC2_INSTANCE_ID="`wget -q -O - http://instance-data/latest/meta-data/instance-id || die \"wget instance-id has failed: $?\"`"
test -n "$EC2_INSTANCE_ID" || die 'cannot obtain instance-id'
EC2_AVAIL_ZONE="`wget -q -O - http://instance-data/latest/meta-data/placement/availability-zone || die \"wget availability-zone has failed: $?\"`"
test -n "$EC2_AVAIL_ZONE" || die 'cannot obtain availability-zone'
EC2_REGION="`echo \"$EC2_AVAIL_ZONE\" | sed -e 's:\([0-9][0-9]*\)[a-z]*\$:\\1:'`"

echo Stop instance $EC2_INSTANCE_ID \( $EC2_REGION \)

read -p "Are you sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
  aws --region $EC2_REGION ec2 stop-instances --instance-ids $EC2_INSTANCE_ID
fi

