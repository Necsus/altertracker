import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { PlayerBgaModel } from '../01_models/03_business/player-bga.model';
import { PlayerModel } from '../01_models/03_business/player.model';
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
}
