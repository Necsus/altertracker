import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { CardModel } from '../01_models/03_business/card.model';
import { CardService } from '../03_business/card.service';
import { CardGroupComponent } from './card-group/card-group.component';
import { SearchPanelComponent } from './search-panel/search-panel.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  imports: [CommonModule, SearchPanelComponent, CardGroupComponent]
})
export class HomeComponent implements OnInit {
  cards: CardModel[] = [];
  groupedCards: { [key: string]: CardModel[] } = {};
  nbCards: number = 0;

  constructor(private cardService: CardService) { }

  ngOnInit(): void {
    this.cardService.count_all_cards$().subscribe({
      next: (count: number) => {
        this.nbCards = count;
      },
      error: (error) => {
        console.error('Error fetching card count:', error);
      }
    });
  }

  onCardsRetrieved(cards: CardModel[]): void {
    this.cards = cards;
    this.groupCardsByName();
  }

  groupCardsByName(): void {
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
