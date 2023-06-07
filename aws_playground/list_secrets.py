#!/bin/python
import boto3
from botocore.config import Config




region = None

regions = ['us-west-1', 'us-east-1', 'us-east-2']



def enumerate_secrets():
    for r in regions:
        print("\n\n-------------\n\nRegion: " + r)
        client = boto3.client('secretsmanager', config=get_config(r))
        secrets = client.list_secrets()
        for s in secrets['SecretList']:
            print(s)

def main():
    enumerate_secrets()


def get_config(region):
    my_config = Config(
    region_name = region,
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
    )
    return my_config



if __name__ == '__main__':
    main()
