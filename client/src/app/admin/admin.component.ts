import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { environment } from '../../environments/environment';
import { SocketService } from './socket.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css'],
  imports: [CommonModule],
})
export class AdminComponent implements OnInit {
  socketConnected: boolean = false;
  status: 'idle' | 'running' | 'success' | 'error' = 'idle';
  logs: string = '';
  subscriptions: Subscription[] = [];

  constructor(
    private http: HttpClient,
    private socketService: SocketService,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit() {
    // Écouter les connexions
    const connectSub = this.socketService.onConnect().subscribe(() => {
      console.log('🟢 Connecté au serveur WebSocket');
      this.socketConnected = true;
    });
    this.subscriptions.push(connectSub);

    // Écouter les déconnexions
    const disconnectSub = this.socketService.onDisconnect().subscribe(() => {
      console.log('🔴 Déconnecté du serveur WebSocket' + '\n');
      this.socketConnected = false;
    });
    this.subscriptions.push(disconnectSub);

    // Écouter les logs
    const serverLogsSub = this.socketService.getScriptOutput().subscribe((message: any) => {
      if (message.data.includes('[flush=True]')) {
        // Remplacer ou ajouter sur la même ligne
        const cleanMessage = this.parseAnsiToHtml(message.data);
        const lastLineIndex = this.logs.lastIndexOf('\n');
        if (lastLineIndex !== -1) {
          this.logs = this.logs.substring(0, lastLineIndex + 1) + cleanMessage; // Remplace la dernière ligne
        } else {
          this.logs += cleanMessage + '\n'; // Si aucune ligne, remplace tout
        }
      } else {
        const cleanMessage = this.parseAnsiToHtml(message.data);
        // Ajouter une nouvelle ligne pour les autres messages
        this.logs += cleanMessage + '\n';
      }

      this.status = 'running';
      this.cdr.detectChanges();
    });
    this.subscriptions.push(serverLogsSub);

    // Écouter les erreurs
    const serverErrorSub = this.socketService.getScriptError().subscribe((err: any) => {
      this.logs += err.error + '\n';
      this.status = 'error';
    });
    this.subscriptions.push(serverErrorSub);

    // Écouter la fin du script
    const serverFinishSub = this.socketService.getScriptFinished().subscribe(() => {
      this.logs += 'Le script est terminé' + '\n';
      this.status = 'success';
    });
    this.subscriptions.push(serverFinishSub);
  }

  parseAnsiToHtml(ansiText: string): string {
    return ansiText
      .replace(/\x1b\[92m/g, '<span class="text-green-500">') // Vert
      .replace(/\x1b\[91m/g, '<span class="text-red-500">')  // Rouge
      .replace(/\x1b\[94m/g, '<span class="text-blue-500">') // Bleu
      .replace('[flush=True]', '')
      .replace(/\x1b\[0m/g, '</span>');                      // Réinitialisation
  }

  ngOnDestroy() {
    this.subscriptions.forEach((sub) => sub.unsubscribe());
  }

  runScript(script_name: string) {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}` // Remplacez 'your-token-here' par le token réel
    });
    this.http.get(`${environment.api_url}/script/start/${script_name}`, { headers }).subscribe({
      next: () => {
        this.status = 'running';
      }
    });
  }
}