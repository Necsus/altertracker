import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { Socket } from 'ngx-socket-io';
import { AuthViewService } from '../../authentication/auth-view.service';

@Component({
  selector: 'app-message',
  templateUrl: './message.component.html',
  styleUrls: ['./message.component.css'],
  imports: [CommonModule, FormsModule, RouterModule]
})
export class MessageComponent implements OnInit {
  messages: any[] = []; // Remplacez any par le type approprié pour vos messages
  selectedUserId!: number; // ID de l'utilisateur sélectionné
  messageText: string = ''; // Texte du message à envoyer
  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private socket: Socket
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });

    this.socket.on('connect_messaging', () => console.log('Connecté au WebSocket'));
    this.socket.on('new_message', (data) => {
      console.log('Nouveau message reçu:', data);
      this.messages.push(data); // afficher le message
    });
  }

  sendMessage() {
    this.socket.emit('private_message', {
      to: this.selectedUserId,
      content: this.messageText
    });
  }
}

