import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Socket } from 'ngx-socket-io';
import { ChatMessage } from '../01_models/03_business/chat-message.model';
import { ChatRoom } from '../01_models/03_business/chat-room.model';
import { ChatService } from '../03_business/chat.service';
import { AuthViewService } from '../authentication/auth-view.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  imports: [CommonModule, FormsModule],
})
export class ChatComponent implements OnInit {
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
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
    this.chatService.get_rooms$().subscribe((rooms: ChatRoom[]) => {
      this.rooms = rooms;
    });
  }

  scrollToBottom() {
    if (this.scrollContainer) {
      const element = this.scrollContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    }
  }

  sendMessage() {
    if (!this.activeRoom || !this.newMessage.trim()) return;
    const messageData = {
      room_id: this.activeRoom.id,
      content: this.newMessage.trim()
    };
    this.chatService.send_message$(messageData).subscribe(() => {
      const newMessage: ChatMessage = {
        sender: 'me',
        content: messageData.content,
        sent_at: new Date()
      };
      this.activeRoom?.messages.push(newMessage);
      this.socket.emit('send_mesage', messageData);
      setTimeout(() => {
        this.scrollToBottom();
      }, 100);
    });
    this.newMessage = '';
  }

  selectRoom(room: ChatRoom) {
    this.activeRoom = room;
    this.socket.emit('join_room', { room_id: room.id });
    this.socket.fromEvent('new_message').subscribe((msg: any) => {
      if (this.activeRoom && msg.room_id === this.activeRoom.id) {
        const newMessage: ChatMessage = {
          sender: msg.sender,
          content: msg.content,
          sent_at: new Date(msg.sent_at)
        };
        this.activeRoom.messages.push(newMessage);
        setTimeout(() => {
          this.scrollToBottom();
        }, 100);
      }
    });
    setTimeout(() => {
      this.scrollToBottom();
    }, 100);
  }

  closeRoom(chatRoom: ChatRoom) {
    this.chatService.closeRoom(chatRoom.id).subscribe(() => {
      chatRoom.is_open = false;
    });
  }
}

