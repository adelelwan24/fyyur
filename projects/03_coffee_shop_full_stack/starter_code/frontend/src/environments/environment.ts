/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:3000', // the running FLASK api server url
  auth0: {
    url: 'dr-doom.eu', // the auth0 domain prefix
    audience: 'coffee_shop_drinks', // the audience set for the auth0 app
    clientId: 'Tx7bHj4hceIev6resSPrjUQUMi48JanS', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
