import { Injectable } from '@angular/core';
import { CanActivate } from '@angular/router';
import { Observable, of } from 'rxjs';
import { AuthApiService } from '../../02_api/auth-api.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { AuthStorageService } from '../services/auth-storage.service';

@Injectable({
  providedIn: 'root'
})
export class TokenGuard implements CanActivate {
  constructor(
    private authStorageService: AuthStorageService,
    private authApiService: AuthApiService,
    private authViewService: AuthViewService
  ) { }

  canActivate(): Observable<boolean> {
    const token = this.authStorageService.getToken();

    if (!token) {
      this.authViewService.logout();
      return of(false);
    }

    if (this.isTokenExpired(token)) {
      this.authViewService.logout();
      return of(false); // Bloque l'accès à la route
    }

    // Si le token est valide, autorise l'accès
    return of(true);
  }

  private isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp && payload.exp < currentTime;
    } catch (e) {
      return true; // Considère le token comme expiré en cas d'erreur
    }
  }
}