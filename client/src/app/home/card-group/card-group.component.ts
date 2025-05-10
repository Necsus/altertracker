import { Component } from '@angular/core';
import { CardComponent } from '../card/card.component';

@Component({
  selector: 'app-card-group',
  templateUrl: './card-group.component.html',
  imports: [CardComponent]
})
export class CardGroupComponent {
  isGroupOpen: { [key: string]: boolean } = {};

  toggleGroup(groupId: string) {
    this.isGroupOpen[groupId] = !this.isGroupOpen[groupId];
  }
}