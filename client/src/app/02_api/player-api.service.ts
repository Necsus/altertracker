import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
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
}
