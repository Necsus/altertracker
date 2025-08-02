import { Component, HostListener, Input } from '@angular/core';
import { ModalService } from './modal.service';

@Component({
  selector: 'app-modal',
  templateUrl: './modal.component.html',
  styleUrls: ['modal.component.css'],
  standalone: true
})
export class ModalComponent {
  @Input() closeOnBackdrop = true;

  constructor(private modalService: ModalService) { }

  onBackdropClick(): void {
    if (this.closeOnBackdrop) {
      this.modalService.closeAll();
    }
  }

  @HostListener('document:keydown.escape')
  onEscapeKey(): void {
    this.modalService.closeAll();
  }
}