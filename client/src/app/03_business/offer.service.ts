import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { OfferViewModel } from '../01_models/home/home-view.model';
import { OfferApiService } from '../02_api/offer-api.service';

@Injectable({
  providedIn: 'root'
})
export class OfferService {
  constructor(private offerApiService: OfferApiService) { }

  get_last_added_offers$(): Observable<OfferViewModel[]> {
    return this.offerApiService.get_last_added_offers$().pipe(map((response: OfferViewModel[]) => {
      return response;
    }));
  }
  get_last_edited_offers$(): Observable<OfferViewModel[]> {
    return this.offerApiService.get_last_edited_offers$().pipe(map((response: OfferViewModel[]) => {
      return response;
    }));
  }
  get_last_deleted_offers$(): Observable<OfferViewModel[]> {
    return this.offerApiService.get_last_deleted_offers$().pipe(map((response: OfferViewModel[]) => {
      return response;
    }));
  }
}