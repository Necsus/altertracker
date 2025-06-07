import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { jwtDecode, JwtPayload } from 'jwt-decode';
import { BehaviorSubject } from 'rxjs';
import { AuthStorageService } from '../00_common/services/auth-storage.service';
import { AuthService } from '../03_business/auth.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Injectable({ providedIn: 'root' })
export class AuthViewService {
  loggedIn = new BehaviorSubject<boolean>(this.isTokenValid());
  isLoggedIn$ = this.loggedIn.asObservable();
  private refreshTimeout: any;

  constructor(
    private authStorageService: AuthStorageService,
    private authService: AuthService,
    private toastService: ToastService,
    private router: Router) { }

  isAdmin(): boolean {
    const token = localStorage.getItem('access_token');
    if (!token) return false;

    try {
      const decoded: any = jwtDecode(token);
      return decoded.is_admin || false;
    } catch (err) {
      console.error('Error decoding token', err);
      return false;
    }
  }

  // Récupérer le username
  getUsername(): string | null {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const decoded: any = jwtDecode(token);
      return decoded.username || null;
    } catch (err) {
      console.error('Error decoding token', err);
      return null;
    }
  }

  // Récupérer le username
  getDiscordIdLinked(): boolean | null {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const decoded: any = jwtDecode(token);
      return decoded.did_linked || null;
    } catch (err) {
      console.error('Error decoding token', err);
      return null;
    }
  }

  logout() {
    this.authService.logout$().subscribe({
      next: () => {
        clearTimeout(this.refreshTimeout);
        this.authStorageService.clearAccessToken();
        this.loggedIn.next(false);
        this.router.navigate(['/login']);
      },
      error: (err: any) => {
        clearTimeout(this.refreshTimeout);
        this.authStorageService.clearAccessToken();
        this.loggedIn.next(false);
        this.router.navigate(['/login']);
      }
    });
  }

  refreshToken() {
    if (this.isTokenExpired() === null) {
      return;
    }

    if (!this.isTokenExpired()) {
      this.authService.refresh_token$().subscribe({
        next: () => {
          this.loggedIn.next(true);
        },
        error: (err: any) => {
          console.error('Error refreshing token', err);
          this.logout();
        }
      });
    } else {
      console.warn('Token is expired, logging out');
      this.logout();
    }
  }

  private isTokenExpired(): boolean | null {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp && payload.exp < currentTime;
      } catch (e) {
        return true; // Considère le token comme expiré en cas d'erreur
      }
    } else {
      return null;
    }
  }

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
}
