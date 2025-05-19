export interface OfferLiveMarketRequest {
  reference: string;
  status: string;
  offerId?: string;
  price?: number;
  currency?: string;
}