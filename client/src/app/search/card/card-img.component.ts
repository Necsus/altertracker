import { Component, Input } from '@angular/core';
import { ModalComponent } from '../../shared/services/modal/modal.component';

@Component({
  standalone: true,
  selector: 'app-card-img',
  templateUrl: './card-img.component.html',
  imports: [ModalComponent]
})
export class CardImgComponent {
  @Input() src!: string; // URL de l'image
  getSrc(): string {
    // Utilisation du service d'images optimisées
    return 'https://www.altered.gg/_next/image?url=' + this.src.replace(/^\/+/, '') + '&w=3840&q=75';
  }
}