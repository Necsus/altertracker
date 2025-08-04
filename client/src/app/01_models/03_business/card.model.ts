import { OfferPurchase } from "./offer-purchase.model";
import { UserAlertModel } from "./user-alert.model";

export interface CardModel {
  id: number;
  id_card: string;
  reference: string;
  name: string;
  name_en?: string;
  faction: string;
  rarity: string;
  type: string;
  set: string;
  subtype?: string;
  imagePath: string;
  image_path_en?: string;
  isSuspended: boolean;
  MAIN_COST: number;
  RECALL_COST: number;
  MOUNTAIN_POWER?: number;
  OCEAN_POWER?: number;
  FOREST_POWER?: number;
  MAIN_EFFECT?: string;
  main_effect_en?: string;
  ECHO_EFFECT?: string;
  echo_effect_en?: string;
  created_at?: string; // ISO date string
  edited_at?: string; // ISO date string
  price?: number;
  price_currency?: string;
  price_updated_at?: string; // ISO date string
  url_offer?: string;
  errated?: boolean;

  alert_id?: number;
  visible?: boolean;
  isProcessing?: boolean;

  purchase_offers?: OfferPurchase[]; // Optional, can be undefined
  mine_purchase_offers?: OfferPurchase[]; // Optional, can be undefined
  alert?: UserAlertModel;
}
