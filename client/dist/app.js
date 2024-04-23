// Import necessary libraries
const AmazonCognitoIdentity = require('amazon-cognito-identity-js');
if (typeof fetch !== 'function') {
    global.fetch = require('node-fetch'); // Required only in Node.js environment
}

// Use global APP_CONFIG from config.js or another configuration source
const { USER_POOL_ID, CLIENT_ID } = window.APP_CONFIG;

const poolData = {
    UserPoolId: USER_POOL_ID,  // Use constants directly
    ClientId: CLIENT_ID        // Use constants directly
};

// Cognito User Pool
const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

// Register event listener for the registration form
document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    var attributeList = [];
    var dataEmail = { Name: 'email', Value: email };
    var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);
    attributeList.push(attributeEmail);

    userPool.signUp(email, password, attributeList, null, function(err, result) {
        if (err) {
            alert(err.message || JSON.stringify(err));
            return;
        }
        alert('Check your email for the verification code.');
        console.log('user name is ' + result.user.getUsername());
    });
});

// Register event listener for the confirmation form
document.getElementById('confirmForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('confirmEmail').value;
    const code = document.getElementById('confirmCode').value;

    const userData = { Username: email, Pool: userPool };
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

    cognitoUser.confirmRegistration(code, true, function(err, result) {
        if (err) {
            alert(err.message || JSON.stringify(err));
            return;
        }
        alert('Registration confirmed!');
        console.log('call result: ' + result);
    });
});

// Register event listener for the login form
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('emailLogin').value;
    const password = document.getElementById('passwordLogin').value;

    const authenticationData = { Username: email, Password: password };
    const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);

    const userData = { Username: email, Pool: userPool };
    const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function(result) {
            const accessToken = result.getAccessToken().getJwtToken();
            const idToken = result.getIdToken().getJwtToken();
        
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('userToken', idToken);
        
            console.log('Login successful. Tokens stored in localStorage.');
            console.log('Access Token:', localStorage.getItem('accessToken'));
            console.log('ID Token:', localStorage.getItem('userToken'));


            setTimeout(function() {
                window.location.href = 'dashboard.html';  // Delay redirect to ensure storage
            }, 1000);  // Adjust time as necessary for testing
        },
        onFailure: function(err) {
            alert(err.message || JSON.stringify(err));
        }
    });
});
