const AWS = require('aws-sdk');
const fs = require('fs');
const path = require('path');
const region = 'eu-west-1';

// Configure AWS SDK
AWS.config.update({
  region
});

const cloudformation = new AWS.CloudFormation();
const stackName = process.env.STACK_NAME;
const configFilePath = path.join(__dirname, '..', 'client', 'dist', 'config.js');

function writeConfig(userPoolId, identityPoolId, clientId, apiUrl) {
  const content = `
  window.APP_CONFIG = {
    USER_POOL_ID: "${userPoolId}",
    IDENTITY_POOL_ID: "${identityPoolId}",
    CLIENT_ID: "${clientId}",
    API_URL: "${apiUrl}",
    REGION: "${region}",
  };
  `;
  fs.mkdirSync(path.dirname(configFilePath), { recursive: true });
  fs.writeFileSync(configFilePath, content);
  console.log('Config file written successfully with UserPool, IdentityPool IDs, and API URL');
}

cloudformation.describeStacks({ StackName: stackName }, (err, data) => {
  if (err) {
    console.error("Failed to retrieve stack data:", err);
    return;
  }
  
  const outputs = data.Stacks[0].Outputs;
  const userPoolId = outputs.find(o => o.OutputKey === 'UserPoolId').OutputValue;
  const identityPoolId = outputs.find(o => o.OutputKey === 'IdentityPoolId').OutputValue;
  const clientId = outputs.find(o => o.OutputKey === 'UserPoolClientId').OutputValue;
  const apiUrlOutput = outputs.find(o => o.OutputKey === 'ApiUrl');
  if (!apiUrlOutput) {
    console.error('ApiGatewayUrl output not found in CloudFormation stack.');
    return; // Exit the function or handle this case appropriately
  }
  const apiUrl = apiUrlOutput.OutputValue;
  
  // Use the IDs and API URL to write the configuration file
  writeConfig(userPoolId, identityPoolId, clientId, apiUrl);
});
