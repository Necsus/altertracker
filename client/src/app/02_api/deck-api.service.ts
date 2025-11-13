import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Param } from '../01_models/02_api/param.model';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class DeckApiService {
  private controller = 'decks';

  constructor(private webApiService: WebApiService) { }

  get_deck$(deck_id: string, include_cards: boolean = true): Observable<any> {
    const params: Param[] = [
      { name: 'include_cards', value: include_cards.toString() }
    ];
    return this.webApiService.callGet$(this.controller, deck_id, params);
  }

  get_player_decks$(
    player_id: string,
    season?: number,
    faction?: string,
    page: number = 1,
    limit: number = 50
  ): Observable<any> {
    const params: Param[] = [
      { name: 'page', value: page.toString() },
      { name: 'limit', value: limit.toString() }
    ];

    if (season) {
      params.push({ name: 'season', value: season.toString() });
    }
    if (faction) {
      params.push({ name: 'faction', value: faction });
    }

    return this.webApiService.callGet$(this.controller, `player/${player_id}`, params);
  }

  compare_decks$(deck1_id: string, deck2_id: string): Observable<any> {
    const params: Param[] = [
      { name: 'deck1', value: deck1_id },
      { name: 'deck2', value: deck2_id }
    ];

    return this.webApiService.callGet$(this.controller, 'compare', params);
  }

  get_meta_snapshot$(season: number, faction?: string): Observable<any> {
    const params: Param[] = [
      { name: 'season', value: season.toString() }
    ];

    if (faction) {
      params.push({ name: 'faction', value: faction });
    }

    return this.webApiService.callGet$(this.controller, 'meta/snapshot', params);
  }

  get_deck_stats$(season?: number): Observable<any> {
    const params: Param[] = [];

    if (season) {
      params.push({ name: 'season', value: season.toString() });
    }

    return this.webApiService.callGet$(this.controller, 'stats', params);
  }

  search_archetypes$(faction?: string, hero?: string, min_games: number = 10): Observable<any> {
    const params: Param[] = [
      { name: 'min_games', value: min_games.toString() }
    ];

    if (faction) {
      params.push({ name: 'faction', value: faction });
    }
    if (hero) {
      params.push({ name: 'hero', value: hero });
    }

    return this.webApiService.callGet$(this.controller, 'archetype/search', params);
  }

  get_archetype$(archetype_id: string): Observable<any> {
    return this.webApiService.callGet$(this.controller, `archetype/${archetype_id}`);
  }
}
