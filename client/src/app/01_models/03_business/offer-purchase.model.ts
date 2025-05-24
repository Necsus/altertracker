import { CardModel } from "./card.model";

export interface OfferPurchase {
  id: number;
  reference_card: string;
  id_user: number;
  price: number;
  currency: string;
  created_at: string;
  is_accepted: boolean | null;
  accepted_at: string | null;

  username?: string;
  card?: CardModel
}
