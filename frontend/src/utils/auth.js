import decode from 'jwt-decode'
import axios from 'axios'
import * as AmazonCognitoIdentity from 'amazon-cognito-identity-js';
const AUTH_TOKEN_KEY = 'authToken'


export function loginUser(username, password, UserPoolId, ClientId) {
   console.log("started login user");
   var authenticationData = {
      Username: username,
      Password: password
   };
   var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
   var poolData = {
      UserPoolId: UserPoolId,
      ClientId: ClientId
   };
   var userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

   var userData = {
      Username: username,
      Pool: userPool
   };
   var cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
   cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: function (result) {

         var accessToken = result.getIdToken().getJwtToken();
        
         setAuthToken(accessToken)
console.log(getAuthToken)
         if (isLoggedIn()) {
           window.location.href = '/';
         }

      },
      onFailure: function (err) {
         //isSubmitted =false;
         window.alert("Incorrect Username/Password");
         console.log(err)
      }
   });
   console.log("completed user login");

}




export function logoutUser() {
   clearAuthToken()
}

export function setAuthToken(token) {
   console.log('Setting token: ' + token)
   axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
   localStorage.setItem(AUTH_TOKEN_KEY, token)
   let sub = getTokenSub(token)
   console.log(`sub: ${sub}`)
}

export function getAuthToken() {
   return localStorage.getItem(AUTH_TOKEN_KEY)
}

export function clearAuthToken() {
   console.log('Clearing auth token')
   axios.defaults.headers.common['Authorization'] = ''
   localStorage.removeItem(AUTH_TOKEN_KEY)
}

export function isLoggedIn() {

   let authToken = getAuthToken()
   let isLoggedIn = !!authToken && !isTokenExpired(authToken)
   console.log(`isLoggedIn: ${isLoggedIn}`)
   return isLoggedIn
}


export function getUserInfo() {
   if (isLoggedIn()) {
      return decode(getAuthToken())
   }
}

export function getUsername() {
   if (isLoggedIn()) {
      let token = decode(getAuthToken())
      if (!token.username) {
         return null
      }

      return token.username
   }
}

function getTokenSub(encodedToken) {
   let token = decode(encodedToken)
   if (!token.sub) {
      return null
   }

   return token.sub
}

function getTokenExpirationDate(encodedToken) {
   let token = decode(encodedToken)
   if (!token.exp) {
      return null
   }

   let date = new Date(0)
   date.setUTCSeconds(token.exp)

   return date
}

function isTokenExpired(token) {
   let expirationDate = getTokenExpirationDate(token)
   return expirationDate < new Date()
}
