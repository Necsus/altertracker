import { CommonModule } from '@angular/common';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CardModel } from '../../01_models/03_business/card.model';
import { CardComponent } from '../card/card.component';

@Component({
  selector: 'app-card-group',
  templateUrl: './card-group.component.html',
  imports: [CommonModule, CardComponent]
})
export class CardGroupComponent implements OnChanges {
  @Input() groupName!: string;
  @Input() cards: CardModel[] = [];
  @Input() autoOpen: boolean = false;
  isGroupOpen: boolean = false;
  displayedCards: number = 100;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['autoOpen'] && this.autoOpen) {
      this.isGroupOpen = true; // Ouvre automatiquement le groupe
    }
  }

  toggleGroup() {
    this.isGroupOpen = !this.isGroupOpen;
  }

  loadMore() {
    this.displayedCards += 100;
  }
}