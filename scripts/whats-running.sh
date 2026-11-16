#!/usr/bin/env bash
# End-of-session check: lists anything that costs money while it is running.
# Uses only free "describe" API calls.
#
# Usage:  bash scripts/whats-running.sh [region]
set -uo pipefail

REGION="${1:-${AWS_REGION:-us-east-2}}"
export AWS_REGION="$REGION"
found=0

# Print a section only if the command returned something.
section() {
  local title="$1"; shift
  local out
  out="$("$@" 2>/dev/null | sed '/^\s*$/d')"
  if [[ -n "$out" && "$out" != "None" ]]; then
    echo "== $title =="
    echo "$out"
    echo ""
    found=1
  fi
}

echo "Checking billable resources in $REGION ..."
echo ""

section "EC2 instances (running)" \
  aws ec2 describe-instances \
    --filters Name=instance-state-name,Values=running \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`Name`]|[0].Value]' \
    --output text

section "NAT Gateways" \
  aws ec2 describe-nat-gateways \
    --filter Name=state,Values=available,pending \
    --query 'NatGateways[].[NatGatewayId,VpcId]' --output text

section "Elastic IPs" \
  aws ec2 describe-addresses \
    --query 'Addresses[].[PublicIp,AllocationId,AssociationId]' --output text

section "VPC interface endpoints" \
  aws ec2 describe-vpc-endpoints \
    --filters Name=vpc-endpoint-type,Values=Interface \
    --query 'VpcEndpoints[].[VpcEndpointId,ServiceName]' --output text

section "Load balancers" \
  aws elbv2 describe-load-balancers \
    --query 'LoadBalancers[].[LoadBalancerName,Type,State.Code]' --output text

section "RDS instances" \
  aws rds describe-db-instances \
    --query 'DBInstances[].[DBInstanceIdentifier,DBInstanceClass,DBInstanceStatus]' --output text

for cluster in $(aws ecs list-clusters --query 'clusterArns[]' --output text 2>/dev/null); do
  services=$(aws ecs list-services --cluster "$cluster" --query 'serviceArns[]' --output text 2>/dev/null)
  [[ -z "$services" ]] && continue
  section "ECS services in ${cluster##*/} (desired > 0)" \
    aws ecs describe-services --cluster "$cluster" --services $services \
      --query 'services[?desiredCount>`0`].[serviceName,desiredCount,runningCount]' --output text
done

section "Unattached EBS volumes" \
  aws ec2 describe-volumes --filters Name=status,Values=available \
    --query 'Volumes[].[VolumeId,Size,VolumeType]' --output text

if [[ $found -eq 0 ]]; then
  echo "Nothing billable found running. You're clear."
else
  echo "Above resources are still running. If you're done for the day:"
  echo "  cd infra/envs/dev && terraform destroy"
  exit 1
fi
