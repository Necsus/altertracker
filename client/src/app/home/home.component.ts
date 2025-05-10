import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { CardModel } from '../00_models/02_business/card.model';
import { CardGroupComponent } from './card-group/card-group.component';
import { SearchPanelComponent } from './search-panel/search-panel.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  imports: [CommonModule, SearchPanelComponent, CardGroupComponent]
})
export class HomeComponent {
  cards: CardModel[] = [];
  groupedCards: { [key: string]: CardModel[] } = {};

  onCardsRetrieved(cards: CardModel[]) {
    this.cards = cards;
    this.groupCardsByName();
  }

  groupCardsByName() {
    this.groupedCards = this.cards.reduce((groups, card) => {
      const name = card.name || 'Unknown';
      if (!groups[name]) {
        groups[name] = [];
      }
      groups[name].push(card);
      return groups;
    }, {} as { [key: string]: CardModel[] });
  }
}
