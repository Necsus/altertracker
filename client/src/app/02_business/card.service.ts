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

  search_cards$(name: string, effect: string, cost: string): Observable<CardModel[]> {
    return this.cardApiService.search_cards$(name, effect, cost).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }
}