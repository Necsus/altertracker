import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private connectSubject = new Subject<boolean>();
  private disconnectSubject = new Subject<boolean>();
  constructor(private socket: Socket) { }

  // Observable pour les connexions
  onConnect(): Observable<boolean> {
    return new Observable((observer) => {
      this.socket.on('connect', () => {
        observer.next(true);
      });
    });
  }

  // Observable pour les déconnexions
  onDisconnect(): Observable<boolean> {
    return new Observable((observer) => {
      this.socket.on('disconnect', () => {
        observer.next(true);
      });
    });
  }

  // Écouter l'événement `server_message`
  getServerMessage(): Observable<any> {
    return this.socket.fromEvent('server_message');
  }

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