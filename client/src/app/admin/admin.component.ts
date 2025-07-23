import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Socket } from 'ngx-socket-io';
import { Subscription } from 'rxjs';
import { environment } from '../../environments/environment';
import { SocketService } from './socket.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css'],
  imports: [CommonModule, FormsModule],
})
export class AdminComponent implements OnInit, OnDestroy {
  @ViewChild('logsContainer') logsContainer!: ElementRef;
  socketConnected: boolean = false;
  status: 'idle' | 'running' | 'success' | 'error' = 'idle';
  scripts: string[] = [
    'script_get_unique',
    'script_get_no_unique',
    'script_get_en',
    'script_get_offers',
    'script_reload_main_effect'
  ];
  selectedScript: string = 'script_get_offers';
  selectedFaction: string = '';
  selectedWorkers: number = 0;
  logs: string = '';
  subscriptions: Subscription[] = [];
  autoScroll: boolean = true;
  private isAutoScrolling = false;
  constructor(
    private http: HttpClient,
    private socketService: SocketService,
    private socket: Socket
  ) { }

  ngOnInit(): void {
    this.socket.connect();

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
      this.logs += this.parseAnsiToHtml(message.data) + '\n';
      this.status = 'running';
      this.scrollToBottom(); // Faire défiler vers le bas
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

  ngOnDestroy(): void {
    this.subscriptions.forEach((sub) => sub.unsubscribe());
    this.socket.disconnect();
  }

  runScript(): void {
    let url = `${environment.api_url}/script/start/${this.selectedScript}`;
    if (this.selectedScript === 'script_get_unique' ||
      this.selectedScript === 'script_get_en' ||
      this.selectedScript === 'script_get_offers' ||
      this.selectedScript === 'script_reload_main_effect') {
      if (this.selectedWorkers) {
        url += `/${this.selectedWorkers}`;
      }
      if (this.selectedFaction) {
        url += `/${this.selectedFaction}`;
      }
    }
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}` // Remplacez 'your-token-here' par le token réel
    });
    this.http.get(url, { headers }).subscribe({
      next: () => {
        this.status = 'running';
      }
    });
  }
  clearLogs(): void {
    this.logs = '';
  }
  onLogsScroll(): void {
    if (this.isAutoScrolling) {
      // Ignore le scroll déclenché par scrollToBottom
      this.isAutoScrolling = false;
      return;
    }
    const el = this.logsContainer.nativeElement;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 5;
    this.autoScroll = atBottom;
  }
  private scrollToBottom(): void {
    if (this.logsContainer && this.autoScroll) {
      this.isAutoScrolling = true;
      setTimeout(() => {
        this.logsContainer.nativeElement.scrollTop = this.logsContainer.nativeElement.scrollHeight;
      }, 0);
    }
  }
}