export interface OfferLiveMarketRequest {
  reference: string;
  status: string;
  offerId?: string;
  convertedPrice?: number;
  convertedCurrency?: string;
}