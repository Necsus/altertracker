export interface OfferPurchase {
  id: string;
  reference_card: string;
  id_user: number;
  price: number;
  currency: string;
  created_at: string;
  is_accepted: boolean | null;
  accepted_at: string | null;

  username?: string;
}
