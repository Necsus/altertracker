import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
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
}
