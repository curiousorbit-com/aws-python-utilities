import os
import boto3
import botocore
import argparse


def start_session(profile=None, region=None):
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

    try:
        aws_region = AWS_DEFAULT_REGION
        if region:
            aws_region = region

        if profile:
            boto_session = boto3.Session(
                profile_name=profile,
                region_name=aws_region
            )
        else:
            boto_session = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=aws_region
            )
        return boto_session
    except botocore.exceptions.ClientError as error:
        print('Invalid profile: {}'.format(profile))
        raise error


def list_instances(resource):
    for instance in resource.instances.all():
        print(f"ID: {instance.id}, State: {instance.state['Name']}, Type: {instance.instance_type}")


def start_instance(resource, instance_id):
    try:
        print(f'Starting {instance_id}...')
        resource.instances.filter(InstanceIds=[instance_id]).start()
        print(f'Start command sent for {instance_id}')
    except botocore.exceptions.ClientError as e:
        print(e)


def stop_instance(resource, instance_id):
    try:
        print(f'Stopping {instance_id}...')
        resource.instances.filter(InstanceIds=[instance_id]).stop()
        print(f'Stop command sent for {instance_id}')
    except botocore.exceptions.ClientError as e:
        print(e)


def terminate_instance(resource, instance_id):
    try:
        print(f'Terminating {instance_id}...')
        resource.instances.filter(InstanceIds=[instance_id]).terminate()
        print(f'Terminate command sent for {instance_id}')
    except botocore.exceptions.ClientError as e:
        print(e)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Manage EC2 instances.')
    parser.add_argument('-l', '--list', action='store_true', help='List all instances')
    parser.add_argument('-s', '--start', type=str, help='Start an instance with given ID')
    parser.add_argument('-p', '--stop', type=str, help='Stop an instance with given ID')
    parser.add_argument('-t', '--terminate', type=str, help='Terminate an instance with given ID')
    parser.add_argument('-pr', '--profile', type=str, help='Specify an AWS CLI config profile.')
    parser.add_argument('-r', '--region', type=str, help='Specify the AWS region where the command will run.')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    if args.profile and args.region:
        session = start_session(args.profile, args.region)
    elif args.profile:
        session = start_session(args.profile)
    else:
        session = start_session()

    # Create an EC2 resource object
    ec2 = session.resource('ec2')

    if args.list:
        list_instances(ec2)
    elif args.start:
        start_instance(ec2, args.start)
    elif args.stop:
        stop_instance(ec2, args.stop)
    elif args.terminate:
        terminate_instance(ec2, args.terminate)
    else:
        print("No arguments provided. Use '-h' or '--help' for usage information.")
