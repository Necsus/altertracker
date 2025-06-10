import { CardModel } from "./card.model";

export interface OfferPurchase {
  id: number;
  reference_card: string;
  id_user: number;
  price: number;
  currency: string;
  created_at: string;
  contacted_at: string | null;
  room_id: string | null;

  username?: string;
  card?: CardModel
}
