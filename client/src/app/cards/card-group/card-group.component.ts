import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
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
  @Output() visibleCardsChange = new EventEmitter<CardModel[]>(); // Émet les cartes visibles
  isGroupOpen: boolean = false;
  displayedCards: number = 100;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['autoOpen'] && this.autoOpen) {
      this.isGroupOpen = true; // Ouvre automatiquement le groupe
    }
    this.emitVisibleCards();
  }

  toggleGroup() {
    this.isGroupOpen = !this.isGroupOpen;
    this.emitVisibleCards();
  }

  loadMore() {
    this.displayedCards += 100;
    this.emitVisibleCards();
  }

  private emitVisibleCards() {
    const visibleCards = this.cards.slice(0, this.displayedCards); // Cartes actuellement visibles
    if (this.isGroupOpen) {
      this.visibleCardsChange.emit(visibleCards);
    }
  }
}