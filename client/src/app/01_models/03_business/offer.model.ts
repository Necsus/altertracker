import { CardModel } from './card.model';

export interface OfferModel {
  id: number;
  referenceCard: string;
  idOffer: string;
  price: number | null;
  currency: string | null;
  quantity: number | null;
  status: string | null;
  linkOffer: string | null;
  isEdited: boolean;
  isDeleted: boolean;
  createdAt: string | null; // ISO string format
  editedAt: string | null;  // ISO string format
  deletedAt: string | null; // ISO string format
  userAltered: string | null;
  userId: number | null;

  card: CardModel | null;
}