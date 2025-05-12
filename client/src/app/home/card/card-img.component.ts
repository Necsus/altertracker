import { Component, Input } from '@angular/core';

@Component({
  standalone: true,
  selector: 'app-card-img',
  templateUrl: './card-img.component.html'
})
export class CardImgComponent {
  @Input() src!: string; // URL de l'image
}