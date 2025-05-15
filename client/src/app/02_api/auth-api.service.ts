import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class AuthApiService {

  private controller = 'auth';

  constructor(private wabApiService: WebApiService) { }

  register$(username: string, email: string, password: string): Observable<any> {
    return this.wabApiService.callPost$(this.controller, 'register', { username: username, email: email, password: password });
  }

  login$(email: string, password: string): Observable<{ access_token: string, refresh_token: string }> {
    return this.wabApiService.callPost$(this.controller, 'login', { email: email, password: password });
  }

  // Rafraîchit le token d'accès avec le refresh token
  refresh$(): Observable<{ access_token: string }> {
    return this.wabApiService.callPost$(this.controller, 'refresh', {}, 110000, true);
  }

  // Envoie un email pour réinitialiser le mot de passe
  forgotPassword$(email: string): Observable<any> {
    return this.wabApiService.callPost$(this.controller, 'forgot-password', { email: email });
  }

  // Réinitialise le mot de passe avec un token reçu
  resetPassword$(token: string, newPassword: string): Observable<any> {
    return this.wabApiService.callPost$(this.controller, `reset-password/${token}`, { password: newPassword });
  }
}