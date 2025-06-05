import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferPurchase } from '../01_models/03_business/offer-purchase.model';
import { OfferModel } from '../01_models/03_business/offer.model';
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
  search_cards$(request: any): Observable<any> {
    return this.wabApiService.callPost$(this.controller, 'search', request);
  }
  post_offer_live_market$(request: OfferLiveMarketRequest[]): Observable<void> {
    return this.wabApiService.callPost$(this.controller, 'offerlivemarket', request);
  }

  get_last_added_cards$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'lastadded');
  }

  get_card_stats$(reference: string): Observable<{ card: CardModel, offers: OfferModel[], purchases: OfferPurchase[], is_mine: boolean }> {
    return this.wabApiService.callGet$(this.controller, `${reference}/offers`);
  }

  update_card$(card: CardModel): Observable<CardModel> {
    return this.wabApiService.callPut$(this.controller, card.reference, { card: card });
  }
}