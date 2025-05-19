import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component } from '@angular/core';
import { ScriptLogService } from './script-log.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent {
  log = '';

  constructor(private http: HttpClient, private scriptLog: ScriptLogService) {
    this.scriptLog.getLogs().subscribe((msg: any) => {
      this.log += msg.data;
    });

    this.scriptLog.getFinish().subscribe(() => {
      this.log += '\n--- Script terminé ---\n';
    });
  }

  startScript() {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${localStorage.getItem('access_token')}` // Remplacez 'your-token-here' par le token réel
    });
    this.http.get('http://localhost:5000/api/script/start-script', { headers }).subscribe();
  }
}