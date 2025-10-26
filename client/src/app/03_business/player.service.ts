import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { GameModel } from '../01_models/03_business/game.model';
import { PlayerBgaModel } from '../01_models/03_business/player-bga.model';
import { PlayerModel } from '../01_models/03_business/player.model';
import { SeasonModel } from '../01_models/03_business/season.model';
import { PlayerApiService } from '../02_api/player-api.service';

@Injectable({
  providedIn: 'root'
})
export class PlayerService {

  private readonly playerApiService = inject(PlayerApiService);

  search_players$(query: string): Observable<PlayerModel[]> {
    return this.playerApiService.search_players$(query).pipe(map((dbModel: any) => {
      return dbModel.map((player: PlayerModel) => {
        return player;
      });
    }));
  }

  search_players_bga$(query: string): Observable<PlayerModel[]> {
    return this.playerApiService.search_players_bga$(query).pipe(map((dbModel: any) => {
      return dbModel.map((player_bga: PlayerBgaModel) => {
        const player = {
          id: 0,
          bga_id: player_bga.bga_id,
          name: player_bga.name,
          country: player_bga.country,
        };
        return player;
      });
    }));
  }

  import_player_bga$(bga_id: number): Observable<string> {
    return this.playerApiService.import_player_bga$(bga_id).pipe(map((dbModel: string) => {
      return dbModel;
    }));
  }

  get_player_by_id$(player_id: string): Observable<PlayerModel> {
    return this.playerApiService.get_player_by_id$(player_id).pipe(
      map((player: PlayerModel) => {
        return player;
      })
    );
  }

  get_player_history$(player_id: string, season: number): Observable<GameModel[]> {
    return this.playerApiService.get_player_history$(player_id, season).pipe(
      map((games: GameModel[]) => {
        return games;
      })
    );
  }

  get_import_ladder$(season: number): Observable<any> {
    return this.playerApiService.get_import_ladder$(season).pipe(
      map((stats: any) => {
        return stats;
      })
    );
  }

  get_season_stats$(
    season: number,
    page: number = 1,
    limit: number = 100
  ): Observable<any> {
    return this.playerApiService.get_season_stats$(season, page, limit).pipe(
      map((response: any) => {
        return response;
      })
    );
  }

  get_season_info$(): Observable<{ seasons: SeasonModel[], total_players: number }> {
    return this.playerApiService.get_season_info$().pipe(
      map((response: { seasons: SeasonModel[], total_players: number }) => {
        return response;
      })
    );
  }

  get_player_overview$(player_id: string, season: number): Observable<any> {
    return this.playerApiService.get_player_overview$(player_id, season).pipe(
      map((response: any) => {
        return response;
      })
    );
  }
}
