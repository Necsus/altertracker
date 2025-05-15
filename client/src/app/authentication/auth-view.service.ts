import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthViewService {
  loggedIn = new BehaviorSubject<boolean>(this.hasValidToken());

  constructor() { }

  // Vérifie si l'access token existe
  private hasValidToken(): boolean {
    const token = localStorage.getItem('access_token');
    // Tu peux aussi décoder le token pour tester l’expiration ici si tu veux
    return !!token;
  }

  // Observable pour les composants
  isLoggedIn$ = this.loggedIn.asObservable();

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.loggedIn.next(false);
  }
}