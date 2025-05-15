import { Injectable } from '@angular/core';
import { jwtDecode, JwtPayload } from 'jwt-decode';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthViewService {
  loggedIn = new BehaviorSubject<boolean>(this.isTokenValid());

  constructor() { }

  // Vérifie si l'access token existe
  private isTokenValid(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const decoded: JwtPayload = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp !== undefined && decoded.exp > currentTime;
    } catch (err) {
      console.error('Invalid token', err);
      return false;
    }
  }

  // Observable pour les composants
  isLoggedIn$ = this.loggedIn.asObservable();

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.loggedIn.next(false);
  }
}
