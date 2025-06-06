import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { CookieManagerApiService } from '../02_api/cookie-manager-api.service';

@Injectable({
  providedIn: 'root'
})
export class CookieManagerService {
  constructor(private cookieManagerApiService: CookieManagerApiService) { }
  get_token$(): Observable<string> {
    const token = localStorage.getItem('offer_token');
    if (!token) {
      return this.cookieManagerApiService.getToken$().pipe(map((token: any) => {
        localStorage.setItem('offer_token', token.token);
        return token.token;
      }));
    } else {
      return new Observable<string>((observer) => {
        observer.next(token);
        observer.complete();
      });
    }
  }
}
