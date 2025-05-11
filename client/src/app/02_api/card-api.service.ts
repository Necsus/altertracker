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
  count_all_cards$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'count');
  }
  get_card_by_reference$(reference: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, reference);
  }
  search_cards$(name: string, rarity: string, faction: string, set: string,
    main_effect: string, echo_efect: string, main_cost: string,
    recall_cost: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'search?name=' + name + '&rarity=' + rarity + '&faction=' + faction + '&set=' + set +
      '&main_effect=' + main_effect + '&echo_effect=' + echo_efect + '&main_cost=' + main_cost + '&recall_cost=' + recall_cost);
  }
}