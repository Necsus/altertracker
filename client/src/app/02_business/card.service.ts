import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { CardModel } from '../00_models/02_business/card.model';
import { CardApiService } from '../01_api/card-api.service';

@Injectable({
  providedIn: 'root'
})
export class CardService {
  constructor(private cardApiService: CardApiService) { }
  get_card_by_reference$(reference: string): Observable<any> {
    return this.cardApiService.get_card_by_reference$(reference).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }

  search_cards$(
    name: string, rarity: string, faction: string, set: string,
    main_effect: string, echo_effect: string, main_cost: string,
    recall_cost: string): Observable<CardModel[]> {
    return this.cardApiService.search_cards$(name, rarity, faction, set, main_effect, echo_effect, main_cost, recall_cost).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }
}