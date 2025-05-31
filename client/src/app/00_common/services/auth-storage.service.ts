import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthStorageService {
  constructor() { }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  storeAccessToken(accessToken: string) {
    localStorage.setItem('access_token', accessToken);
  }

  clearAccessToken() {
    localStorage.removeItem('access_token');
  }
}