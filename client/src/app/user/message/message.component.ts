import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { Socket } from 'ngx-socket-io';
import { MessageService } from '../../03_business/message.service';
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
    private socket: Socket,
    private messageService: MessageService
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    const token = localStorage.getItem('access_token');

    // Connexion WebSocket avec authentification
    this.socket.emit('connect_messaging', { token: `Bearer ${token}` });

    this.socket.on('new_message', (data) => {
      console.log('Nouveau message reçu:', data);
      this.messages.push(data); // afficher le message
    });

    this.socket.on('message_status_updated', (data) => {
      console.log('Statut du message mis à jour:', data);
      const message = this.messages.find(msg => msg.id === data.message_id);
      if (message) {
        message.status = data.status;
      }
    });

    this.loadMessageHistory();
  }

  loadMessageHistory(): void {
    if (this.selectedUserId) {
      this.messageService.get_message_history$(this.selectedUserId).subscribe({
        next: (messages) => {
          this.messages = messages; // Charger l'historique dans la liste des messages
        }
      });
    }
  }

  sendMessage() {
    if (this.messageText.trim()) {
      const token = localStorage.getItem('access_token');
      this.socket.emit('private_message', {
        token: `Bearer ${token}`,
        to: this.selectedUserId,
        content: this.messageText
      });
      this.messages.push({
        from: 'me',
        content: this.messageText,
        timestamp: new Date().toISOString()
      });
      this.messageText = ''; // Réinitialiser le champ d'entrée
    }
  }
}
