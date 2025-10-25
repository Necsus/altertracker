import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { GameModel } from '../01_models/03_business/game.model';
import { PlayerBgaModel } from '../01_models/03_business/player-bga.model';
import { PlayerModel } from '../01_models/03_business/player.model';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class PlayerApiService {
  private controller = 'player';

  private readonly wabApiService = inject(WebApiService);

  search_players$(query: string): Observable<PlayerModel[]> {
    return this.wabApiService.callGet$(this.controller, `search?query=${query}`);
  }

  search_players_bga$(query: string): Observable<PlayerBgaModel[]> {
    return this.wabApiService.callGet$(this.controller, `searchbga?query=${query}`);
  }

  import_player_bga$(bga_id: number): Observable<string> {
    return this.wabApiService.callGet$(this.controller, `importbga/${bga_id}`);
  }

  get_player_by_id$(player_id: string): Observable<PlayerModel> {
    return this.wabApiService.callGet$(this.controller, player_id);
  }

  get_player_history$(player_id: string): Observable<GameModel[]> {
    return this.wabApiService.callGet$(this.controller, `history/${player_id}`);
  }

  get_season_stats$(season: number): Observable<any> {
    return this.wabApiService.callGet$(this.controller, `importladder/${season}`);
  }
}
