import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Socket } from 'ngx-socket-io';
import { CardModel } from '../01_models/03_business/card.model';
import { ChatMessage } from '../01_models/03_business/chat-message.model';
import { ChatRoom } from '../01_models/03_business/chat-room.model';
import { ChatService } from '../03_business/chat.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { CardImgComponent } from '../cards/card/card-img.component';
import { LocalizedValuePipe } from '../shared/pipes/localized-value.pipe';
import { ModalService } from '../shared/services/modal/modal.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  imports: [CommonModule, FormsModule, LocalizedValuePipe],
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('scrollContainer') scrollContainer!: ElementRef;
  currentLanguage: string = 'fr';
  rooms: ChatRoom[] = [];
  activeRoom: ChatRoom | null = null;
  activeRoomMessages: ChatMessage[] = [];
  newMessage = '';

  constructor(
    private authViewService: AuthViewService,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private chatService: ChatService,
    private socket: Socket,
    private translate: TranslateService,
    private modalService: ModalService) {
    this.currentLanguage = this.translate.currentLang || 'en'; // Définit la langue par défaut
    this.translate.onLangChange.subscribe((event) => {
      this.currentLanguage = event.lang;
    });
  }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    this.chatService.get_rooms$().subscribe((rooms: ChatRoom[]) => {
      this.rooms = rooms;
      const room_id = this.activatedRoute.snapshot.paramMap.get('room_id');
      if (room_id) {
        const room = this.rooms.find(r => r.id === room_id);
        if (room) {
          this.selectRoom(room);
        } else {
          this.activeRoom = null;
          this.activeRoomMessages = [];
        }
      } else {
        this.activeRoom = null;
        this.activeRoomMessages = [];
      }
    });
  }

  ngOnDestroy(): void {
    this.socket.disconnect();
  }

  scrollToBottom() {
    if (this.scrollContainer) {
      const element = this.scrollContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    }
  }

  getMessages(): void {
    this.activeRoomMessages = [];
    if (!this.activeRoom) return;
    this.chatService.get_messages$(this.activeRoom.id).subscribe((messages: ChatMessage[]) => {
      this.activeRoomMessages = messages;
      setTimeout(() => {
        this.scrollToBottom();
      }, 100);
    });
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
      this.activeRoomMessages.push(newMessage);
      this.socket.emit('send_mesage', messageData);
      setTimeout(() => {
        this.scrollToBottom();
      }, 100);
    });
    this.newMessage = '';
  }

  selectRoom(room: ChatRoom) {
    this.activeRoom = room;
    this.socket.connect();
    this.socket.emit('join_room', { room_id: room.id });
    this.socket.fromEvent('new_message').subscribe((msg: any) => {
      if (this.activeRoom && msg.room_id === this.activeRoom.id) {
        const newMessage: ChatMessage = {
          sender: msg.sender,
          content: msg.content,
          sent_at: new Date(msg.sent_at)
        };
        this.activeRoomMessages.push(newMessage);
        setTimeout(() => {
          this.scrollToBottom();
        }, 100);
      }
    });
    this.getMessages();
  }

  closeRoom(chatRoom: ChatRoom) {
    this.chatService.close_room$(chatRoom.id).subscribe(() => {
      chatRoom.is_open = false;
    });
  }

  openModal(card: CardModel): void {
    const currentLanguage = this.translate.currentLang || 'fr';
    this.modalService.open(CardImgComponent, { src: currentLanguage === 'en' ? card.image_path_en : card.imagePath });
  }
}

