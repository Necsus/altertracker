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

  logout() {
    this.authService.logout$().subscribe({
      next: () => {
        clearTimeout(this.refreshTimeout);
        this.authStorageService.clearAccessToken();
        // this.toastService.show('Session expirée. Veuillez vous reconnecter.', 'error', 5000);
        this.loggedIn.next(false);
        this.router.navigate(['/login']);
      }
    });
  }

  startTokenRefresh(): void {
    // Nettoyer le timeout précédent
    if (this.refreshTimeout) {
      clearTimeout(this.refreshTimeout);
    }

    const token = localStorage.getItem('access_token');
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
    console.log(timeUntilRefresh);
    if (timeUntilRefresh > 0) {
      this.refreshTimeout = setTimeout(() => {
        this.refreshToken();
      }, timeUntilRefresh);
    } else {
      this.logout();
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

  refreshToken(): void {
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
      console.log('Decoded payload:', payload);
      return payload.exp ? payload.exp * 1000 : null; // Convertit en millisecondes
    } catch (e) {
      return null;
    }
  }
}
