import os
import boto3

# Get the current AWS credentials
credentials = boto3.Session().get_credentials()

# Create the AWS credentials directory if it doesn't exist
aws_dir = os.path.expanduser('~/.aws')
if not os.path.exists(aws_dir):
    os.makedirs(aws_dir)

# Write the credentials to the AWS credentials file
credential_file = os.path.join(aws_dir, 'credentials')
with open(credential_file, 'w') as f:
    f.write('[default]\n')
    f.write('region=us-west-2\n')
    f.write(f'accessKeyId={credentials.access_key}\n')
    f.write(f'secretAccessKey={credentials.secret_key}\n') 
    if credentials.token:
        f.write(f'sessionToken={credentials.token}\n')