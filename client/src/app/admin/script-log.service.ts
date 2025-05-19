import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ScriptLogService {
  constructor(private socket: Socket) {
    this.socket.on('connect', () => console.log('🟢 CONNECTÉ au WebSocket'));
    this.socket.on('disconnect', () => console.log('🔴 DÉCONNECTÉ'));
  }

  getLogs(): Observable<any> {
    return this.socket.fromEvent('script_output');
  }

  getFinish(): Observable<any> {
    return this.socket.fromEvent('script_finished');
  }
}