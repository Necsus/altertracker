import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthStorageService {
  constructor() { }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  storeTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  storeAccessToken(accessToken: string) {
    localStorage.setItem('access_token', accessToken);
  }
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }
}