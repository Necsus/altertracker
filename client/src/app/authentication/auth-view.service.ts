import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { jwtDecode, JwtPayload } from 'jwt-decode';
import { BehaviorSubject } from 'rxjs';
import { AuthStorageService } from '../00_common/services/auth-storage.service';
import { AuthService } from '../03_business/auth.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Injectable({ providedIn: 'root' })
export class AuthViewService {
  private refreshTimeout: any;
  loggedIn = new BehaviorSubject<boolean>(this.isTokenValid());

  constructor(
    private authService: AuthService,
    private authStorageService: AuthStorageService,
    private toastService: ToastService,
    private router: Router) { }

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
    clearTimeout(this.refreshTimeout);
    this.authStorageService.clearTokens();
    this.toastService.show('Session expirée. Veuillez vous reconnecter.', 'error', 5000);
    this.loggedIn.next(false);
    this.router.navigate(['/login']);
  }

  startTokenRefresh(): void {
    const token = this.authStorageService.getToken();
    if (!token) {
      this.logout();
      return;
    }

    const expirationTime = this.getTokenExpirationTime(token);
    if (!expirationTime) {
      this.logout();
      return;
    }

    const currentTime = Date.now();
    const timeUntilRefresh = expirationTime - currentTime - 60000;

    console.log(timeUntilRefresh);// Rafraîchit 1 minute avant l'expiration

    if (timeUntilRefresh > 0) {
      this.refreshTimeout = setTimeout(() => {
        this.refreshToken();
      }, timeUntilRefresh);
    } else {
      this.refreshToken(); // Rafraîchit immédiatement si le token est déjà proche de l'expiration
    }
  }

  private refreshToken(): void {
    const refreshToken = this.authStorageService.getRefreshToken();
    if (!refreshToken) {
      this.logout();
      return;
    }

    this.authService.refresh$().subscribe({
      next: () => {
        console.log('Token refreshed');
        this.startTokenRefresh(); // Redémarre le cycle de rafraîchissement
      },
      error: () => {
        this.logout();
      }
    });
  }

  private getTokenExpirationTime(token: string): number | null {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp ? payload.exp * 1000 : null; // Convertit en millisecondes
    } catch (e) {
      return null;
    }
  }
}
