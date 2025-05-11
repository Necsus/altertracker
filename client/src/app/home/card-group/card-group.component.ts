import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { CardModel } from '../../00_models/02_business/card.model';
import { CardComponent } from '../card/card.component';

@Component({
  selector: 'app-card-group',
  templateUrl: './card-group.component.html',
  imports: [CommonModule, CardComponent]
})
export class CardGroupComponent {
  @Input() groupName!: string;
  @Input() cards: CardModel[] = [];
  isGroupOpen: boolean = false;

  toggleGroup() {
    this.isGroupOpen = !this.isGroupOpen;
  }
}