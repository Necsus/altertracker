import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class CardApiService {

  private controller = 'card';

  constructor(private wabApiService: WebApiService) {
  }

  get_card_by_reference$(reference: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, reference);
  }
  search_cards$(name: string, effect: string, cost: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'search?name=' + name + '&effect=' + effect + '&cost=' + cost);
  }
}