import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map, Observable } from 'rxjs';
import { ChatMessage } from '../01_models/03_business/chat-message.model';
import { ChatRoom } from '../01_models/03_business/chat-room.model';
import { ChatApiService } from '../02_api/chat-api.service';

@Injectable({ providedIn: 'root' })
export class ChatService {

  constructor(
    private chatApiService: ChatApiService,
    private socket: Socket) { }

  get_rooms$(): Observable<ChatRoom[]> {
    return this.chatApiService.get_rooms$().pipe(map((dbModel: ChatRoom[]) => {
      return dbModel;
    }));
  }

  get_messages$(room_id: string): Observable<ChatMessage[]> {
    return this.chatApiService.get_messages$(room_id).pipe(map((dbModel: ChatMessage[]) => {
      return dbModel;
    }));
  }

  create_room$(purchaseId: number): Observable<string> {
    return this.chatApiService.create_room$(purchaseId).pipe(map((dbModel: any) => {
      return dbModel.room_id;
    }));
  }

  send_message$(messageData: any): Observable<void> {
    return this.chatApiService.send_message$(messageData).pipe(map(() => {
      return undefined;
    }));
  }

  close_room$(room_id: string): Observable<void> {
    return this.chatApiService.close_room$(room_id).pipe(map(() => {
      return undefined;
    }));
  }
}