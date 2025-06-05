import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlteredApiService {

  private baseUrl = 'https://api.altered.gg';

  constructor(private http: HttpClient) { }

  getOfferByReference$(reference: string, token: string): Observable<any> {
    const url = `${this.baseUrl}/cards/${reference}/offers?itemsPerPage=10&page=1`;
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Accept': '*/*'
    });

    return this.http.get<any>(url, { headers }).pipe(
      catchError((error) => {
        if (error.status === 401) {
          console.error(error.message ?? 'Unauthorized');
        }
        return throwError(() => error);
      })
    );
  }
  getCardByReferenceEnglish$(reference: string): Observable<any> {
    const url = `${this.baseUrl}/cards/${reference}?locale=en-en`;
    const headers = new HttpHeaders({
      'Accept': '*/*'
    });

    return this.http.get<any>(url, { headers }).pipe(
      catchError((error) => {
        if (error.status === 404) {
          console.error('Card not found');
        }
        return throwError(() => error);
      })
    );
  }
  getAccessToken$(): Observable<string> {
    const url = `https://www.altered.gg/api/auth/session`;
    const headers = new HttpHeaders({
      'Accept': '*/*'
    });

    return this.http.get<any>(url, { headers, withCredentials: true }).pipe(
      catchError((error) => {
        if (error.status === 404) {
          console.error('Card not found');
        }
        return throwError(() => error);
      })
    );
  }
  getCollection$(token: string, page: number): Observable<any> {
    const url = `${this.baseUrl}/cards?cardType%5B%5D=CHARACTER&collection=true&rarity%5B%5D=UNIQUE&itemsPerPage=36&page=${page}&locale=fr-fr`;
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Accept': '*/*'
    });

    return this.http.get<any>(url, { headers }).pipe(
      catchError((error) => {
        if (error.status === 401) {
          console.error(error.message ?? 'Unauthorized');
        }
        return throwError(() => error);
      })
    );
  }
}