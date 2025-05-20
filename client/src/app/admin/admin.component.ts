import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { SocketService } from './socket.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css'],
  imports: [CommonModule],
})
export class AdminComponent implements OnInit {
  logs: string = '';
  error: string | null = null;
  finished: boolean = false;
  isRunning: boolean = false;

  constructor(
    private http: HttpClient,
    private socketService: SocketService) { }

  ngOnInit() {
    // Écouter les logs
    this.socketService.getScriptOutput().subscribe((msg: any) => {
      this.logs += msg.data + '\n';
    });

    // Écouter les erreurs
    this.socketService.getScriptError().subscribe((err: any) => {
      this.error = err.error;
      this.isRunning = false; // Arrêter l'exécution en cas d'erreur
    });

    // Écouter la fin du script
    this.socketService.getScriptFinished().subscribe(() => {
      this.finished = true;
      this.isRunning = false; // Réinitialiser le statut de l'exécution
    });
  }

  startScript() {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}` // Remplacez 'your-token-here' par le token réel
    });
    this.http.get('http://localhost:5000/api/script/start-script', { headers }).subscribe({
      next: (response) => {
        this.isRunning = true;
        this.logs = ''; // Réinitialiser les logs
        this.error = null; // Réinitialiser l'erreur
        this.finished = false; // Réinitialiser le statut de fin
      }
    });
  }
}