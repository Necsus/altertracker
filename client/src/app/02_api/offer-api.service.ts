import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class OfferApiService {

  private controller = 'offer';

  constructor(private wabApiService: WebApiService) { }

  get_last_added_offers$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'lastadded');
  }
  get_last_edited_offers$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'lastedited');
  }
  get_last_deleted_offers$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'lastdeleted');
  }
}