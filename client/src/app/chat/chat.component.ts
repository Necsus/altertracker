import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Socket } from 'ngx-socket-io';
import { ChatRoom } from '../01_models/03_business/chat-room.model';
import { ChatService } from '../03_business/chat.service';
import { AuthViewService } from '../authentication/auth-view.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  imports: [CommonModule, FormsModule],
})
export class ChatComponent implements OnInit {
  rooms: ChatRoom[] = [];
  activeRoom: ChatRoom | null = null;
  newMessage = '';

  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private chatService: ChatService,
    private socket: Socket) { }

  ngOnInit() {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    this.chatService.get_rooms().subscribe((rooms: ChatRoom[]) => {
      this.rooms = rooms;
    });

    this.chatService.onNewMessage().subscribe((msg) => {
      if (this.activeRoom && msg.conversation_id === this.activeRoom.id) {
        this.activeRoom.messages.push(msg);
      }
    });
  }

  sendMessage() {
    this.socket.emit('send_message', {
      room_id: this.activeRoom?.id,
      // sender_id: data.sender_id,
      content: this.newMessage
    });
    this.newMessage = '';
  }

  selectRoom(room: ChatRoom) {
    this.activeRoom = room;
    this.socket.emit('join_room', { room_id: room.id });
  }

  closeRoom(chatRoom: ChatRoom) {
    this.chatService.closeRoom(chatRoom.id).subscribe(() => {
      chatRoom.is_open = false;
    });
  }
}