import { Injectable } from '@angular/core';
import { map, Observable, of } from 'rxjs';
import { ChatRoom } from '../01_models/03_business/chat-room.model';
import { ChatApiService } from '../02_api/chat-api.service';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private socket: any;

  constructor(private chatApiService: ChatApiService) { }

  get_rooms(): Observable<ChatRoom[]> {
    return this.chatApiService.get_rooms$().pipe(map((dbModel: ChatRoom[]) => {
      return dbModel;
    }));
  }




  connect(discordId: string) {
    // this.socket = io(this.baseUrl);
    // this.socket.emit('join', discordId);
  }



  sendMessage(data: any) {
    this.socket.emit('send_message', data);
  }

  onNewMessage(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('new_message', (msg: any) => {
        observer.next(msg);
      });
    });
  }

  closeRoom(id: string): Observable<void> {
    return of();
    // return this.http.post(`${this.baseUrl}/conversation/${id}/close`, {});
  }
}