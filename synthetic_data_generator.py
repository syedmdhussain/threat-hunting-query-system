"""
Synthetic CloudTrail Data Generator

Generates realistic CloudTrail logs for testing the threat hunting system
when the original Kaggle dataset is unavailable.
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import argparse


class CloudTrailGenerator:
    """Generate synthetic CloudTrail events"""
    
    def __init__(self, seed=42):
        random.seed(seed)
        
        # Realistic data for generation
        self.event_names = [
            'ConsoleLogin', 'GetCallerIdentity', 'RunInstances', 'StopLogging',
            'DeleteTrail', 'GetSecretValue', 'CreateAccessKey', 'GetBucketAcl',
            'DescribeInstances', 'ListBuckets', 'GetUser', 'PutObject', 'GetObject'
        ]
        
        self.event_sources = [
            'signin.amazonaws.com', 'sts.amazonaws.com', 'ec2.amazonaws.com',
            'cloudtrail.amazonaws.com', 'secretsmanager.amazonaws.com',
            'iam.amazonaws.com', 's3.amazonaws.com'
        ]
        
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        
        self.user_agents = [
            'aws-cli/2.0.0 Python/3.8.0 Linux/5.4.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'aws-sdk-go/1.40.0',
            'Boto3/1.18.0 Python/3.9.0',
            'kali-linux/2021.1',  # Suspicious
            'powershell/7.1',  # Suspicious
        ]
        
        self.usernames = ['admin', 'developer', 'analyst', 'service-account', 'root']
        
        self.instance_types = [
            't2.micro', 't2.small', 'm5.large', 'c5.xlarge', 
            'p3.10xlarge',  # Large instance for cryptomining
            'p3.16xlarge'   # Extra large
        ]
        
        self.error_messages = [
            'No username found in supplied account',
            'Failed authentication',
            'Invalid credentials',
            None  # Success
        ]
        
        self.error_codes = [
            'AccessDenied', 'UnauthorizedOperation', None
        ]
    
    def generate_ip(self):
        """Generate random IP address"""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    
    def generate_timestamp(self, start_date, end_date):
        """Generate random timestamp"""
        delta = end_date - start_date
        random_seconds = random.randint(0, int(delta.total_seconds()))
        timestamp = start_date + timedelta(seconds=random_seconds)
        return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def generate_event_id(self):
        """Generate UUID-like event ID"""
        import uuid
        return str(uuid.uuid4())
    
    def generate_arn(self, username, account_id):
        """Generate ARN"""
        return f"arn:aws:iam::{account_id}:user/{username}"
    
    def generate_normal_event(self, start_date, end_date):
        """Generate a normal CloudTrail event"""
        event_name = random.choice([e for e in self.event_names if e not in ['StopLogging', 'DeleteTrail']])
        event_source = random.choice(self.event_sources)
        username = random.choice(self.usernames)
        account_id = str(random.randint(100000000, 999999999))
        
        event = {
            'eventTime': self.generate_timestamp(start_date, end_date),
            'eventName': event_name,
            'eventSource': event_source,
            'sourceIPAddress': self.generate_ip(),
            'userAgent': random.choice([ua for ua in self.user_agents if 'kali' not in ua.lower() and 'powershell' not in ua.lower()]),
            'errorCode': None,
            'errorMessage': None,
            'awsRegion': random.choice(self.regions),
            'userIdentitytype': 'IAMUser' if username != 'root' else 'Root',
            'userIdentityuserName': username,
            'userIdentityarn': self.generate_arn(username, account_id),
            'userIdentityaccountId': account_id,
            'requestParametersinstanceType': None,
            'requestParametersbucketName': None,
            'responseElementsaccessKeyId': None,
            'eventID': self.generate_event_id(),
            'readOnly': str(random.choice([True, False])).lower(),
            'resources': None,
            'recipientAccountId': account_id
        }
        
        # Add specific fields for certain events
        if event_name == 'RunInstances':
            event['requestParametersinstanceType'] = random.choice(self.instance_types[:4])
        
        return event
    
    def generate_threat_event(self, threat_type, start_date, end_date):
        """Generate event matching specific threat hypothesis"""
        
        if threat_type == 'failed_login':
            # Hypothesis 1: Failed console logins
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'ConsoleLogin',
                'eventSource': 'signin.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'Mozilla/5.0',
                'errorCode': 'Failed',
                'errorMessage': random.choice([
                    'No username found in supplied account',
                    'Failed authentication',
                    'Invalid credentials'
                ]),
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'HIDDEN_DUE_TO_SECURITY_REASONS',
                'userIdentityarn': 'arn:aws:iam::123456789:user/test',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'root_console':
            # Hypothesis 2: Root console access
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'ConsoleLogin',
                'eventSource': 'signin.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'Mozilla/5.0',
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'Root',
                'userIdentityuserName': 'root',
                'userIdentityarn': 'arn:aws:iam::123456789:root',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'cloudtrail_disruption':
            # Hypothesis 3: CloudTrail disruption
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': random.choice(['StopLogging', 'DeleteTrail']),
                'eventSource': 'cloudtrail.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'attacker',
                'userIdentityarn': 'arn:aws:iam::123456789:user/attacker',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'unauthorized':
            # Hypothesis 4: Unauthorized API calls
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': random.choice(['RunInstances', 'CreateUser', 'PutObject']),
                'eventSource': random.choice(self.event_sources),
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': random.choice(['AccessDenied', 'UnauthorizedOperation']),
                'errorMessage': 'User is not authorized to perform this action',
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'unauthorized-user',
                'userIdentityarn': 'arn:aws:iam::123456789:user/unauthorized',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'whoami':
            # Hypothesis 5: Reconnaissance (GetCallerIdentity)
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'GetCallerIdentity',
                'eventSource': 'sts.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'recon-user',
                'userIdentityarn': 'arn:aws:iam::123456789:user/recon',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'true',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'secrets':
            # Hypothesis 6: Secrets Manager access
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'GetSecretValue',
                'eventSource': 'secretsmanager.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'secrets-user',
                'userIdentityarn': 'arn:aws:iam::123456789:user/secrets',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'true',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'large_instance':
            # Hypothesis 7: Large EC2 instances (cryptomining)
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'RunInstances',
                'eventSource': 'ec2.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'miner',
                'userIdentityarn': 'arn:aws:iam::123456789:user/miner',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': random.choice(['p3.10xlarge', 'p3.16xlarge', 'p4d.24xlarge']),
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 's3_bruteforce':
            # Hypothesis 8: S3 bucket brute force
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'GetBucketAcl',
                'eventSource': 's3.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': random.choice([None, 'AccessDenied']),
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'scanner',
                'userIdentityarn': 'arn:aws:iam::123456789:user/scanner',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': f'bucket-{random.randint(1000, 9999)}',
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'true',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'suspicious_agent':
            # Hypothesis 9: Suspicious user agents
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': random.choice(self.event_names),
                'eventSource': random.choice(self.event_sources),
                'sourceIPAddress': self.generate_ip(),
                'userAgent': random.choice(['kali-linux/2021.1', 'ParrotOS/4.11', 'powershell/7.1']),
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'attacker',
                'userIdentityarn': 'arn:aws:iam::123456789:user/attacker',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': None,
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        elif threat_type == 'access_key':
            # Hypothesis 10: Permanent key creation
            return {
                'eventTime': self.generate_timestamp(start_date, end_date),
                'eventName': 'CreateAccessKey',
                'eventSource': 'iam.amazonaws.com',
                'sourceIPAddress': self.generate_ip(),
                'userAgent': 'aws-cli/2.0',
                'errorCode': None,
                'errorMessage': None,
                'awsRegion': 'us-east-1',
                'userIdentitytype': 'IAMUser',
                'userIdentityuserName': 'developer',
                'userIdentityarn': 'arn:aws:iam::123456789:user/developer',
                'userIdentityaccountId': '123456789',
                'requestParametersinstanceType': None,
                'requestParametersbucketName': None,
                'responseElementsaccessKeyId': f'AKIA{random.randint(1000000000000000, 9999999999999999)}',
                'eventID': self.generate_event_id(),
                'readOnly': 'false',
                'resources': None,
                'recipientAccountId': '123456789'
            }
        
        return self.generate_normal_event(start_date, end_date)
    
    def generate_dataset(self, num_records=1000, include_threats=True, threat_ratio=0.2):
        """Generate complete synthetic CloudTrail dataset"""
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        events = []
        
        # Calculate threat and normal event counts
        if include_threats:
            num_threats = int(num_records * threat_ratio)
            num_normal = num_records - num_threats
            
            threat_types = [
                'failed_login', 'root_console', 'cloudtrail_disruption',
                'unauthorized', 'whoami', 'secrets', 'large_instance',
                's3_bruteforce', 'suspicious_agent', 'access_key'
            ]
            
            # Generate threat events
            threats_per_type = num_threats // len(threat_types)
            for threat_type in threat_types:
                for _ in range(threats_per_type):
                    events.append(self.generate_threat_event(threat_type, start_date, end_date))
        else:
            num_normal = num_records
        
        # Generate normal events
        for _ in range(num_normal):
            events.append(self.generate_normal_event(start_date, end_date))
        
        # Shuffle events
        random.shuffle(events)
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        # Sort by timestamp
        df = df.sort_values('eventTime').reset_index(drop=True)
        
        return df


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic CloudTrail data')
    parser.add_argument('--num-records', type=int, default=1000, help='Number of records to generate')
    parser.add_argument('--output', type=str, default='data/synthetic_cloudtrail.csv', help='Output file path')
    parser.add_argument('--include-threats', action='store_true', default=True, help='Include threat events')
    parser.add_argument('--threat-ratio', type=float, default=0.2, help='Ratio of threat events (0.0-1.0)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    print(f"Generating {args.num_records} synthetic CloudTrail records...")
    print(f"Threat ratio: {args.threat_ratio if args.include_threats else 0}")
    print(f"Output: {args.output}")
    
    generator = CloudTrailGenerator(seed=args.seed)
    df = generator.generate_dataset(
        num_records=args.num_records,
        include_threats=args.include_threats,
        threat_ratio=args.threat_ratio
    )
    
    # Create output directory if needed
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Save to CSV
    df.to_csv(args.output, index=False)
    
    print(f"\n✓ Generated {len(df)} records")
    print(f"✓ Saved to {args.output}")
    print(f"\nSample records:")
    print(df.head())
    print(f"\nEvent distribution:")
    print(df['eventName'].value_counts())


if __name__ == '__main__':
    main()

