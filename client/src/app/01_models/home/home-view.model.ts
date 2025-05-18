import { CardModel } from '../03_business/card.model';
import { OfferModel } from '../03_business/offer.model';

export interface OfferViewModel {
  current_offer: OfferModel,
  previous_offer?: OfferModel,
  card: CardModel,
}
