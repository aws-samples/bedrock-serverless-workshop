# Create AWS accounts
for i in {18..20}; do
  aws organizations create-account --email prallam+acnt$i@amazon.com --account-name aws-events-acnt$i
done

# Move the accounts into the 'bedrockevent' organizational unit
OU_ID=$(aws organizations list-organizational-units | jq -r '.OrganizationalUnits[] | select(.Name == "bedrockevent").Id')
for i in {18..20}; do
  ACCOUNT_ID=$(aws organizations list-accounts | jq -r '.Accounts[] | select(.Name == "aws-events-acnt'$i'").Id')
  aws organizations move-account --account-id $ACCOUNT_ID --source-parent-id ou-7439 --destination-parent-id $OU_ID
done

aws organizations move-account --account-id 525840005564 --source-parent-id ou-7439 --destination-parent-id ou-7439-16nv0zlq


#Create 5 IAM users CFN call
#aws cloudformation create-stack --stack-name user-setup-DONOT-DELETE --template-body file://gen-ai-builder-init-v1.2.yaml --capabilities CAPABILITY_NAMED_IAM
