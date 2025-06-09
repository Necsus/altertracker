import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ChatMessage } from '../01_models/03_business/chat-message.model';
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

  get_messages$(room_id: string): Observable<ChatMessage[]> {
    return this.wabApiService.callGet$(this.controller, `message/${room_id}`);
  }

  create_room$(purchase_id: number): Observable<any> {
    return this.wabApiService.callGet$(this.controller, `room/create/${purchase_id}`);
  }

  send_message$(message: any): Observable<void> {
    return this.wabApiService.callPost$(this.controller, 'message', message);
  }
}
