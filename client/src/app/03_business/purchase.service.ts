import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { OfferPurchase } from '../01_models/03_business/offer-purchase.model';
import { PurchaseApiService } from '../02_api/purchase-api.service';

@Injectable({
  providedIn: 'root'
})
export class PurchaseService {
  constructor(private purchaseApiService: PurchaseApiService) { }

  getPurchasesByReference$(reference: string): Observable<OfferPurchase[]> {
    return this.purchaseApiService.getPurchasesByReference$(reference).pipe(map((dbModel: OfferPurchase[]) => {
      return dbModel;
    }));;
  }

  getUserPurchases$(): Observable<OfferPurchase[]> {
    return this.purchaseApiService.getUserPurchases$().pipe(map((dbModel: OfferPurchase[]) => {
      return dbModel;
    }));
  }

  postNewPurchase$(request: any): Observable<OfferPurchase> {
    return this.purchaseApiService.postNewPurchase$(request).pipe(map((dbModel: OfferPurchase) => {
      return dbModel;
    }));
  }

  deletePurchase$(purchase_id: number): Observable<void> {
    return this.purchaseApiService.deletePurchase$(purchase_id).pipe(map(() => void 0));
  }
}
