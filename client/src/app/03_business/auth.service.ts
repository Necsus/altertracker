import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { AuthStorageService } from '../00_common/services/auth-storage.service';
import { AuthApiService } from '../02_api/auth-api.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private authApiService: AuthApiService, private authStorageService: AuthStorageService) { }

  register$(username: string, email: string, password: string): Observable<any> {
    return this.authApiService.register$(username, email, password).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  login$(email: string, password: string): Observable<void> {
    return this.authApiService.login$(email, password).pipe(map((response: { access_token: string }) => {
      this.authStorageService.storeAccessToken(response.access_token);
    }));
  }

  logout$(): Observable<any> {
    return this.authApiService.logout$().pipe(map((response: any) => {
      return response;
    }));
  }

  validateEmail$(token: string): Observable<any> {
    return this.authApiService.validateEmail$(token).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  resendValidationEmail$(token: string): Observable<any> {
    return this.authApiService.resendValidationEmail$(token).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  refresh$(): Observable<void> {
    return this.authApiService.refresh$().pipe(map((response: any) => {
      this.authStorageService.storeAccessToken(response.access_token);
    }));
  }

  forgotPassword$(email: string): Observable<any> {
    return this.authApiService.forgotPassword$(email).pipe(map((response: any) => {
      return response;
    }));
  }

  resetPassword$(token: string, newPassword: string): Observable<any> {
    return this.authApiService.resetPassword$(token, newPassword).pipe(map((response: any) => {
      return response;
    }));
  }
}