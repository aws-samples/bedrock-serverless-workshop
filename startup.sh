#!/bin/bash
echo "Preparing Cloud9 for project deploymnet"
# Check if 'CFNStackName' is set in the environment variables
if [ -z "$CFNStackName" ]; then
    echo "Error: 'CFNStackName' environment variable is not set. Please set it and run the script."
    exit 1
fi
echo "CFN Start up stack name: $CFNStackName"


echo "Update ubantu os"
sudo apt-get update

echo "Install jq for cli query operations"
sudo apt install -y jq

#echo "Resize the Cloud9 to 20 GB space"
#cd ~/environment/bedrock-serverless-workshop/tools
#chmod +x resize.sh
#./resize.sh 20

echo "Update node js to version 16"
source "$HOME/.nvm/nvm.sh"
nvm install 16
nvm use 16
node --version

echo "Set region"
export AWS_REGION=$(aws configure get region)
echo "AWS Region is $AWS_REGION"

echo "Build the backend code using sam build"
cd ~/environment/bedrock-serverless-workshop
sam build

echo "Export S3 bucket name and Kendra index which are created as part of Startup CFN stack"
export S3BucketName=$(aws cloudformation describe-stacks --stack-name ${CFNStackName} --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" --output text)
export KendraIndexID=$(aws cloudformation describe-stacks --stack-name ${CFNStackName} --query "Stacks[0].Outputs[?OutputKey=='KendraIndexID'].OutputValue" --output text)

#You can also use these commands to read values
#export S3BucketName=$(aws s3api list-buckets | jq -r --arg bucketName "$CFNStackName" '.Buckets[] | select(.Name | contains($bucketName)) | .Name')
#export KendraIndexID=$(aws kendra list-indices | jq -r --arg indexName "$CFNStackName" '.IndexConfigurationSummaryItems[] | select(.Name | contains($indexName)) | .Id')

export SAMStackName="sam-$CFNStackName"
echo $SAMStackName

echo "Copy toml file and replace the parameters"

cp tools/samconf.toml samconfig.toml
# Replace values in .//samconfig.toml
sed -Ei "s|<KendraIndexId>|${KendraIndexID}|g" ./samconfig.toml
sed -Ei "s|<S3BucketName>|${S3BucketName}|g" ./samconfig.toml
sed -Ei "s|<SAMStackName>|${SAMStackName}|g" ./samconfig.toml
sed -Ei "s|<AWS_REGION>|${AWS_REGION}|g" ./samconfig.toml

echo "Deploy app with sam deploy"
sam deploy

echo "Export few more parameters from the sam stack output"
export BedrockApiUrl=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='BedrockApiUrl'].OutputValue" --output text)
export UserPoolId=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='CognitoUserPool'].OutputValue" --output text)
export UserPoolClientId=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='CongnitoUserPoolClientID'].OutputValue" --output text)
export SecretName=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='SecretsName'].OutputValue" --output text)
echo "API Gateway endpoint: $BedrockApiUrl"
echo "Cognito user pool id: $UserPoolId"
echo "Cognito client id: $UserPoolClientId"
echo "Secret name: $SecretName"

# Replace values in ./backend/samconfig.toml
sed -Ei "s|<ApiGatewayUrl>|${BedrockApiUrl}|g" ./frontend/src/main.js
sed -Ei "s|<CognitoUserPoolId>|${UserPoolId}|g" ./frontend/src/main.js
sed -Ei "s|<UserPoolClientId>|${UserPoolClientId}|g" ./frontend/src/main.js

#Install Ampliyfy and build frontend
echo "Install Ampliyfy and build frontend"
cd ~/environment/bedrock-serverless-workshop/frontend
npm i -S @vue/cli-service
npm i -g @aws-amplify/cli
npm install
npm run build
cp ~/.aws/credentials ~/.aws/config

#Amplify initialization
echo "Amplify initialization"
mv dist build
amplify init --yes


echo "Add hosting, hit enter key if it prompts for action, use default"
amplify add hosting parameters.json

echo "Publish the amplify project"
amplify publish --yes

echo "Save the user_id and password to login to UI"
aws secretsmanager get-secret-value --secret-id $SecretName | jq -r .SecretString
