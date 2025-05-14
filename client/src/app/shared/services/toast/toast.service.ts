import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration: number;
}

@Injectable({
  providedIn: 'root',
})
export class ToastService {
  private toastSubject = new Subject<ToastMessage>();
  toast$ = this.toastSubject.asObservable();

  show(message: string, type: ToastType = 'info', duration: number = 3000) {
    this.toastSubject.next({ id: this.generateId(), message: message, type: type, duration: duration });
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
}