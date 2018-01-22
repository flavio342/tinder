import { Injectable } from '@angular/core';

@Injectable()
export class AuthProvider {

  isLoggedIn = false;

  user;
  tinder_token;

  facebook_credentials = {
    id: "",
    token: ""
  }

  constructor() {
   
  }

}
