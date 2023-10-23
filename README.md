# Amazon Bedrock Serverless Workshop

This project contains source code and supporting files for a serverless application that you can deploy Amazon Bedrock Serverless solution using the SAM CLI. In this, you use the Retrieval-Augmented Generation (RAG) technique to build a generative AI-powered chatbot. A foundation model (FM) in Amazon Bedrock is used to answer your chatbot questions through pre-indexed content. Amazon Bedrock is a fully managed service that makes FMs (from Amazon and leading AI startups) available through an API, so you can choose from various FMs to find the model that's best suited to your use case. For storing (indexing) and retrieving relevant content, you use Amazon Kendra, a fully managed service that provides intelligent enterprise searches powered by machine learning. You use AWS Lambda as the serverless compute for running the application code in an event-driven manner.

The project includes the following files and folders.
- **Bedrock Function:** Code for the application's RAG Lambda function, and also a function for authenticating the app.
- **UI code:** The code is developed using Amazon Amplify with Vue JavaScript framework.
- **Sam Template:** A template (template.yaml) that defines the application's AWS backend resources. Once you run this using SAM, it creates Amazon API Gateway endpoint, AWS Lambda function (RAG), and a Amazon Cognito user pool.

## Deploy and test Amazon Bedrock serverless application

To deploy and test this code, visit the following Amazon Bedrock workshop.

See the [Creating a Serverless Chatbot using Amazon Bedrock](https://studio.us-east-1.prod.workshops.aws/preview/27eb3134-4f33-4689-bb73-269e4273947a/builds/48e535f7-43d6-4498-b6dc-95530d0002b3/en-US) 

## Resources

- [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [Amazon Kendra developer guide](https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html)
- [Amazon Bedrock user guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

