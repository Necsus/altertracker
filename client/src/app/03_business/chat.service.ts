import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { map, Observable, of } from 'rxjs';
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

  connect(discordId: string) {
    // this.socket = io(this.baseUrl);
    // this.socket.emit('join', discordId);
  }

  onNewMessage(): Observable<any> {
    return this.socket.fromEvent('new_message');
  }

  closeRoom(id: string): Observable<void> {
    return of();
    // return this.http.post(`${this.baseUrl}/conversation/${id}/close`, {});
  }
}