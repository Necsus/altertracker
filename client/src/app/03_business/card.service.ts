import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { EffectModel } from '../01_models/03_business/effect.model';
import { OfferPurchase } from '../01_models/03_business/offer-purchase.model';
import { OfferModel } from '../01_models/03_business/offer.model';
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

  search_cards$(request: any): Observable<CardModel[]> {
    return this.cardApiService.search_cards$(request).pipe(map((dbModel: any) => {
      return dbModel.map((card: CardModel) => {
        if (card.price && card.price > 0) {
          card.visible = true;
        }
        return card;
      });
    }));
  }

  post_offer_live_market$(offers: OfferLiveMarketRequest[]): Observable<void> {
    const request = {
      from_script: false,
      offers: offers
    }
    return this.cardApiService.post_offer_live_market$(request).pipe(map(() => void 0));
  }

  get_last_added_cards$(): Observable<{ count: number, cards: CardModel[] }> {
    return this.cardApiService.get_last_added_cards$().pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  get_card_stats$(reference: string): Observable<{ card: CardModel, offers: OfferModel[], purchases: OfferPurchase[], is_mine: boolean }> {
    return this.cardApiService.get_card_stats$(reference).pipe(map((dbModel: { card: CardModel, offers: OfferModel[], purchases: OfferPurchase[], is_mine: boolean }) => {
      return dbModel;
    }));
  }

  updateCard$(card: CardModel): Observable<CardModel> {
    return this.cardApiService.update_card$(card).pipe(map((dbModel: CardModel) => {
      return dbModel;
    }));
  }

  getEffect$(lang: string): Observable<EffectModel[]> {
    return this.cardApiService.get_effects$(lang).pipe(map((dbModel: EffectModel[]) => {
      return dbModel;
    }));
  }

  getCardsBatch$(references: string[]): Observable<{ [key: string]: any }> {
    return this.cardApiService.get_cards_batch$(references).pipe(
      map((response: { cards: { [key: string]: any } }) => response.cards)
    );
  }
}