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
}