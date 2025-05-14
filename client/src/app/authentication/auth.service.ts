import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = 'http://localhost:5000/api/auth';

  constructor(private http: HttpClient) { }

  login(email: string, password: string) {
    return this.http.post<{ access_token: string }>(`${this.api}/login`, { email, password });
  }

  register(email: string, password: string) {
    return this.http.post(`${this.api}/register`, { email, password });
  }

  forgotPassword(email: string) {
    return this.http.post(`${this.api}/forgot-password`, { email });
  }

  resetPassword(token: string, password: string) {
    return this.http.post(`${this.api}/reset-password/${token}`, { password });
  }

  storeToken(token: string) {
    localStorage.setItem('access_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}