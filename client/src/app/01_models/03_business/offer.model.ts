import { CardModel } from './card.model';

export interface OfferModel {
  id: number;
  referenceCard: string;
  id_offer: string;
  price: number | null;
  currency: string | null;
  status: string | null;
  link_offer: string | null;
  is_deleted: boolean;
  created_at: string | null; // ISO string format
  deleted_at: string | null; // ISO string format
  user_altered: string | null;
  userId: number | null;
  previous_offer: number | null;

  card: CardModel | null;
}