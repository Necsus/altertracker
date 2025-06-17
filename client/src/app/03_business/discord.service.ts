import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { DiscordApiService } from '../02_api/discord-api.service';


@Injectable({
  providedIn: 'root'
})
export class DiscordService {
  constructor(private discordApiService: DiscordApiService) { }
  callback$(code: string): Observable<any> {
    return this.discordApiService.discord_callback$(code).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }
  unlink$(): Observable<void> {
    return this.discordApiService.discord_unlink$().pipe(map(() => {
      return;
    }));
  }
}
