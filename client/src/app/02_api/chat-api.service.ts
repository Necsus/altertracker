import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ChatRoom } from '../01_models/03_business/chat-room.model';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class ChatApiService {

  private controller = 'chat';

  constructor(private wabApiService: WebApiService) { }

  get_rooms$(): Observable<ChatRoom[]> {
    return this.wabApiService.callGet$(this.controller, 'room');
  }
}
