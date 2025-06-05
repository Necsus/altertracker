import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class CookieManagerApiService {

  private controller = 'cookie-manager';

  constructor(
    private wabApiService: WebApiService
  ) {
  }
  getToken$(): Observable<string> {
    return this.wabApiService.callGet$(this.controller, 'getaccesstoken');
  }
}
