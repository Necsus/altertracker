import { CardModel } from '../03_business/card.model';
import { OfferViewModel } from './offer-view.model';

export interface HomeViewModel {
  last_added_cards_count?: number,
  last_aded_cards?: CardModel[],

  last_added_offers_count?: number,
  last_added_offers?: OfferViewModel[],

  last_edited_offers_count?: number,
  last_edited_offers?: OfferViewModel[],

  last_deleted_offers_count?: number,
  last_deleted_offers?: OfferViewModel[],
}
