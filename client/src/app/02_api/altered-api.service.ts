import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlteredApiService {

  private baseUrl = 'https://api.altered.gg/cards';

  constructor(private http: HttpClient) { }

  getOfferByReference(reference: string, token: string): Observable<any> {
    const url = `${this.baseUrl}/${reference}/offers?itemsPerPage=10&page=1`;
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