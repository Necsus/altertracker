import { CardModel } from './card.model';

export interface UserCollectionModel {
  id: number;
  id_user: number;
  reference_card: string;
  added_at: Date;
  card: CardModel;
}
