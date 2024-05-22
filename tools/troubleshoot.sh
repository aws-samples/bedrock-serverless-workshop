#!/bin/bash

#### FIRT RUN ALL THESE ###
export CFNStackName=bedrock-chatbot-hs
export S3BucketName=$(aws cloudformation describe-stacks --stack-name ${CFNStackName} --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" --output text)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
export KendraIndexID=$(aws cloudformation describe-stacks --stack-name ${CFNStackName} --query "Stacks[0].Outputs[?OutputKey=='KendraIndexID'].OutputValue" --output text)
export SAMStackName="sam-$CFNStackName"
export BedrockApiUrl=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='BedrockApiUrl'].OutputValue" --output text)
export SecretName=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='SecretsName'].OutputValue" --output text)


#Amplify and sam builds
nvm use 16
node --version

#update Ampliyfy and build frontend
cd ~/environment/bedrock-serverless-workshop/frontend
npm run build
#npm install marked

rm -r build
mv dist build
amplify publish --yes

### SAM deployments
cd ~/environment/bedrock-serverless-workshop
sam build
sam deploy

aws secretsmanager get-secret-value --secret-id $SecretName | jq -r .SecretString

https://dev.d3pro0sb2mjyj9.amplifyapp.com/

