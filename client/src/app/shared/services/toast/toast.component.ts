import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ToastMessage, ToastService } from './toast.service';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css'],
  imports: [CommonModule]
})
export class ToastComponent implements OnInit {
  toasts: ToastMessage[] = [];

  constructor(private toastService: ToastService) { }

  ngOnInit(): void {
    this.toastService.toast$.subscribe(toast => {
      this.toasts.push(toast);
      setTimeout(() => this.removeToast(toast), toast.duration);
    });
  }

  removeToast(toast: ToastMessage) {
    this.toasts = this.toasts.filter(t => t !== toast);
  }
}