import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class DiscordApiService {
  private controller = 'discord';

  constructor(private wabApiService: WebApiService) {
  }
  discord_callback$(code: string): Observable<any> {
    return this.wabApiService.callPost$(this.controller, 'callback', { code: code });
  }
}
