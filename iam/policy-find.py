import boto3
import botocore.exceptions
from aws_sso_lib import get_boto3_session
import json

SSO_START_URL = '<INSERT SSO URL>'
SSO_REGION = '<INSERT SSO REGION>'
AWS_ACCOUNT_ID = '<INSERT AWS ACCOUNT ID>'
AWS_ACCOUNT_ROLE = '<INSERT AWS ACCOUNT ROLE>'
AWS_ACCOUNT_REGION = '<INSERT AWS REGION>'

action_to_find = 'lambda:GetFunction'
policy_list = []


def main():
    policy_evaluated_count = 0
    policy_affected_count = 0

    # Connect to the account
    boto3_sso_session = get_boto3_session(SSO_START_URL, SSO_REGION,
                                          AWS_ACCOUNT_ID, AWS_ACCOUNT_ROLE,
                                          region=AWS_ACCOUNT_REGION,
                                          login=True)

    iam_client = boto3_sso_session.client('iam')

    # Build a list of all attached policies that contain
    paginator = iam_client.get_paginator('list_policies')

    for page in paginator.paginate(Scope='All', OnlyAttached=True):
        policies = page['Policies']
        for policy in policies:
            policy_evaluated_count += 1
            # Get the ARN for each policy
            policy_arn = policy['Arn']
            # Get the default version for each of the policies
            policy_version = iam_client.get_policy(
                    PolicyArn=policy_arn)['Policy']['DefaultVersionId']
            # Get the policy document
            policy_document = iam_client.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=policy_version)['PolicyVersion']['Document']

            # Convert the policy document to JSON
            policy_json = json.dumps(policy_document)

            if action_to_find in policy_json:
                policy_affected_count += 1
                policy_list.append(policy_arn)

    iam_client.close()

    print(f'Total policies evaulated: {policy_evaluated_count}')
    print(f'Total policies affected: {policy_affected_count}')
    for item in policy_list:
        print(f'The policy {item} contains the action in question')


main()
