export interface CardModel {
  id: string;
  reference: string;
  name: string;
  name_en?: string;
  faction: string;
  rarity: string;
  type: string;
  set: string;
  imagePath: string;
  isSuspended: boolean;
  MAIN_COST: number;
  RECALL_COST: number;
  MOUNTAIN_POWER?: number;
  OCEAN_POWER?: number;
  FOREST_POWER?: number;
  MAIN_EFFECT?: string;
  ECHO_EFFECT?: string;
  created_at?: string; // ISO date string
  edited_at?: string;  // ISO date string
}
