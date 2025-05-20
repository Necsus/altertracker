import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  constructor(private socket: Socket) { }

  // Écouter les logs du script
  getScriptOutput(): Observable<any> {
    return this.socket.fromEvent('script_output');
  }

  // Écouter les erreurs du script
  getScriptError(): Observable<any> {
    return this.socket.fromEvent('script_error');
  }

  // Écouter la fin du script
  getScriptFinished(): Observable<any> {
    return this.socket.fromEvent('script_finished');
  }
}