import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
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
  count_all_cards_in_market$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'inmarketcount');
  }
  get_card_by_reference$(reference: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, reference);
  }
  search_cards$(name: string, rarity: string, faction: string, set: string,
    main_effect: string, main_effect_2: string, echo_efect: string, main_cost: string,
    recall_cost: string, forest_power: string, mountain_power: string, ocean_power: string,
    in_market: string, no_condition: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'search',
      [
        { name: 'name', value: name },
        { name: 'rarity', value: rarity },
        { name: 'faction', value: faction },
        { name: 'set', value: set },
        { name: 'main_effect', value: main_effect },
        { name: 'main_effect_2', value: main_effect_2 },
        { name: 'echo_efect', value: echo_efect },
        { name: 'main_cost', value: main_cost },
        { name: 'recall_cost', value: recall_cost },
        { name: 'forest_power', value: forest_power },
        { name: 'mountain_power', value: mountain_power },
        { name: 'ocean_power', value: ocean_power },
        { name: 'in_market', value: in_market },
        { name: 'no_condition', value: no_condition },
      ]);
  }
  post_offer_live_market$(request: OfferLiveMarketRequest[]): Observable<void> {
    return this.wabApiService.callPost$(this.controller, 'offerlivemarket', request);
  }
}