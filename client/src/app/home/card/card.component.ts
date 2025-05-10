import { Component } from '@angular/core';

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html'
})
export class CardComponent {
  isModalOpen = false;
  modalImageSrc = '';

  openModal(imgSrc: string) {
    this.modalImageSrc = imgSrc;
    this.isModalOpen = true;
  }

  closeModal() {
    this.isModalOpen = false;
  }
}
