import { Component, Input } from '@angular/core';
import { CardModel } from '../../01_models/03_business/card.model';

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html'
})
export class CardComponent {
  @Input() card!: CardModel; // Données de la carte
  isModalOpen = false;
  modalImageSrc = '';

  refreshPrice(): void {
    // Logique pour rafraîchir le prix de la carte
    console.log('Rafraîchir le prix de la carte :', this.card.name);
  }

  // openModal(imgSrc: string) {
  //   this.modalImageSrc = imgSrc;
  //   this.isModalOpen = true;
  // }

  // closeModal() {
  //   this.isModalOpen = false;
  // }
}
