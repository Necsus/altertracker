export interface OfferLiveMarketRequest {
  id: number;
  reference: string;
  status: string;
  offerId?: string;
  convertedPrice?: number;
  convertedCurrency?: string;
  quantity?: number;
}