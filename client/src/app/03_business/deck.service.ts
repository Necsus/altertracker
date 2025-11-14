import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { CardModel } from '../01_models/03_business/card.model';
import { DeckApiService } from '../02_api/deck-api.service';

export interface DeckModel {
  id: string;
  player_id: string;
  deck_name: string;
  faction: string;
  hero: string;
  season: number;
  card_count: number;
  unique_count: number;
  rare_count: number;
  total_games: number;
  total_wins: number;
  total_losses: number;
  draws: number;
  win_rate: number;
  deck_signature: string;
  archetype_id?: string;
  archetype_name?: string;
  cards_by_uid?: { [key: string]: number };
  unique_cards?: string[];
  cards_data?: { [key: string]: CardModel };
  created_at: string;
  last_used_at: string;
}

export interface DeckComparisonModel {
  deck1: DeckModel;
  deck2: DeckModel;
  comparison: {
    similarity: number;
    same_archetype: boolean;
    cards_in_common: number;
    cards_different: number;
    unique_differences: string[];
    effect_differences: string[];
  };
}

export interface ArchetypeModel {
  id: string;
  name: string;
  faction: string;
  hero: string;
  total_decks: number;
  total_games: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  play_rate: number;
}

export interface MetaSnapshotModel {
  season: number;
  faction?: string;
  meta: {
    archetype: ArchetypeModel;
    play_rate: number;
    win_rate: number;
    total_games: number;
  }[];
}

@Injectable({
  providedIn: 'root'
})
export class DeckService {
  private readonly deckApiService = inject(DeckApiService);

  get_deck$(deck_id: string, include_cards: boolean = true): Observable<DeckModel> {
    return this.deckApiService.get_deck$(deck_id, include_cards).pipe(
      map((deck: DeckModel) => deck)
    );
  }

  get_player_decks$(
    player_id: string,
    season?: number,
    faction?: string,
    page: number = 1,
    limit: number = 50
  ): Observable<{ decks: DeckModel[]; pagination: any }> {
    return this.deckApiService.get_player_decks$(player_id, season, faction, page, limit).pipe(
      map((response: any) => response)
    );
  }

  compare_decks$(deck1_id: string, deck2_id: string): Observable<DeckComparisonModel> {
    return this.deckApiService.compare_decks$(deck1_id, deck2_id).pipe(
      map((comparison: DeckComparisonModel) => comparison)
    );
  }

  get_meta_snapshot$(season: number, faction?: string): Observable<MetaSnapshotModel> {
    return this.deckApiService.get_meta_snapshot$(season, faction).pipe(
      map((meta: MetaSnapshotModel) => meta)
    );
  }

  get_deck_stats$(season?: number): Observable<any> {
    return this.deckApiService.get_deck_stats$(season).pipe(
      map((stats: any) => stats)
    );
  }

  search_archetypes$(faction?: string, hero?: string, min_games: number = 10): Observable<{ archetypes: ArchetypeModel[]; total: number }> {
    return this.deckApiService.search_archetypes$(faction, hero, min_games).pipe(
      map((response: any) => response)
    );
  }
}
