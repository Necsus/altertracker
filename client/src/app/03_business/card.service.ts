import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { CardApiService } from '../02_api/card-api.service';

@Injectable({
  providedIn: 'root'
})
export class CardService {
  constructor(private cardApiService: CardApiService) { }
  count_all_cards$(): Observable<number> {
    return this.cardApiService.count_all_cards$().pipe(map((dbModel: any) => {
      return dbModel.count;
    }));
  }

  count_all_cards_in_market$(): Observable<number> {
    return this.cardApiService.count_all_cards_in_market$().pipe(map((dbModel: any) => {
      return dbModel.count;
    }));
  }

  get_card_by_reference$(reference: string): Observable<any> {
    return this.cardApiService.get_card_by_reference$(reference).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  search_cards$(
    name: string, rarity: string, faction: string, set: string,
    main_effect: string, main_effect_2: string, echo_effect: string, main_cost: string,
    recall_cost: string, in_market: string, no_condition: string): Observable<CardModel[]> {
    return this.cardApiService.search_cards$(name, rarity, faction, set, main_effect, main_effect_2, echo_effect, main_cost, recall_cost, in_market, no_condition).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  post_offer_live_market$(request: OfferLiveMarketRequest[]): Observable<void> {
    return this.cardApiService.post_offer_live_market$(request).pipe(map(() => void 0));
  }
}