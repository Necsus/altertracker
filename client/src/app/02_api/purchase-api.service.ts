import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferPurchase } from '../01_models/03_business/offer-purchase.model';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class PurchaseApiService {

  private controller = 'purchase';

  constructor(private wabApiService: WebApiService) { }

  getPurchasesByReference$(reference: string): Observable<OfferPurchase[]> {
    return this.wabApiService.callGet$(this.controller, `reference/${reference}`);
  }

  getUserPurchases$(): Observable<CardModel[]> {
    return this.wabApiService.callGet$(this.controller, 'mine');
  }

  postNewPurchase$(request: any): Observable<OfferPurchase> {
    return this.wabApiService.callPost$(this.controller, '', request);
  }

  deletePurchase$(purchase_id: number): Observable<void> {
    return this.wabApiService.callDelete$(this.controller, `${purchase_id}`);
  }
}
