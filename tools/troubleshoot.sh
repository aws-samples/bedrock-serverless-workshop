#!/bin/bash

#### FIRT RUN ALL THESE ###
export CFNStackName=bedrock-ws954
export S3BucketName=$(aws cloudformation describe-stacks --stack-name ${CFNStackName} --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" --output text)
export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')
export KendraIndexID=$(aws cloudformation describe-stacks --stack-name ${CFNStackName} --query "Stacks[0].Outputs[?OutputKey=='KendraIndexID'].OutputValue" --output text)
export SAMStackName="sam-$CFNStackName"
export BedrockApiUrl=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='BedrockApiUrl'].OutputValue" --output text)
export SecretName=$(aws cloudformation describe-stacks --stack-name ${SAMStackName} --query "Stacks[0].Outputs[?OutputKey=='SecretsName'].OutputValue" --output text)


#Amplify and sam builds
#nvm use 16
#node --version


export PATH=~/.npm-global/bin:$PATH

#update Ampliyfy and build frontend
cd ~/environment/bedrock-serverless-workshop/frontend
npm run build

rm -r build
mv dist build
amplify publish --yes

### SAM deployments
cd ~/environment/bedrock-serverless-workshop
sam build && sam deploy

aws secretsmanager get-secret-value --secret-id $SecretName | jq -r .SecretString

export KB_ID=$(aws bedrock-agent list-knowledge-bases | jq -r '.knowledgeBaseSummaries[0].knowledgeBaseId')
echo "Knowledge Base ID: $KB_ID"
sed -Ei "s|copy_kb_id|${KB_ID}|g" ./template.yaml

