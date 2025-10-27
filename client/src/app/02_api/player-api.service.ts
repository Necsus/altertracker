import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { GameModel } from '../01_models/03_business/game.model';
import { PlayerBgaModel } from '../01_models/03_business/player-bga.model';
import { PlayerModel } from '../01_models/03_business/player.model';
import { SeasonModel } from '../01_models/03_business/season.model';
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
    return this.wabApiService.callGet$(this.controller, `importbga/${bga_id}`, undefined, 1800000); // 30 minutes
  }

  get_player_by_id$(player_id: string): Observable<PlayerModel> {
    return this.wabApiService.callGet$(this.controller, player_id, undefined, 1800000);
  }

  get_player_history$(player_id: string, season: number): Observable<GameModel[]> {
    return this.wabApiService.callGet$(this.controller, `history/${player_id}?season=${season}`);
  }

  get_import_ladder$(season: number): Observable<any> {
    return this.wabApiService.callGet$(this.controller, `importladder/${season}`, undefined, 1800000); // 30 minutes
  }

  get_season_stats$(
    season: number,
    page: number = 1,
    limit: number = 100,
    includePlayer: boolean = true
  ): Observable<any> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      include_player: includePlayer.toString()
    });

    return this.wabApiService.callGet$(
      this.controller,
      `ladder/${season}?${params.toString()}`
    );
  }

  get_season_info$(): Observable<{ seasons: SeasonModel[], total_players: number }> {
    return this.wabApiService.callGet$(this.controller, 'infos');
  }

  get_player_overview$(player_id: string, season: number): Observable<any> {
    return this.wabApiService.callGet$(this.controller, `overview/${player_id}?season=${season}`);
  }

  get_player_reload$(player_id: string): Observable<any> {
    return this.wabApiService.callGet$(this.controller, `reload/${player_id}`, undefined, 1800000); // 30 minutes
  }
}
