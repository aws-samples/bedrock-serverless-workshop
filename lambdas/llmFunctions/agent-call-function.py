import boto3

region = boto3.session.Session().region_name

def lambda_handler(event, context):
    boto3_version = boto3.__version__
    print(f"Boto3 version: {boto3_version}")
    
    #bedrock = boto3.client('bedrock')
    bedrock_agent_client = boto3.client('bedrock-agent')


    # Invoke the agent
    response = bedrock_agent_client.invoke_agent(
        agentId='customer-agent-demos',
        inputText='How AI will help in use of Digital Implants? What is the timeframe to achieve that?'
    )

    # Process the agent's response
    agent_response = response['response']
    print(agent_response)

    return {
        'statusCode': 200,
        'body': agent_response
    }
