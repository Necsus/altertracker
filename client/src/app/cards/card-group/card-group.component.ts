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
  @Input() allGroupsOpen: boolean = false;
  @Input() getMarketComplete: boolean = true; // Indique si le marché est complet
  @Output() visibleCardsChange = new EventEmitter<CardModel[]>(); // Émet les cartes visibles
  isGroupOpen: boolean = false;
  displayedCards: number = 50;
  onlyCardsWithPrice: boolean = false;

  get visibleCards(): CardModel[] {
    if (this.onlyCardsWithPrice) {
      return this.cards.filter(card => card.visible);
    }
    return this.cards;
  }

  // Méthode pour gérer le changement de la case à cocher
  onOnlyCardsWithPrice(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.onlyCardsWithPrice = input.checked; // Met à jour la valeur de la case à cocher
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['autoOpen'] && this.autoOpen) {
      this.isGroupOpen = true; // Ouvre automatiquement le groupe
      this.emitVisibleCards();
    }
    if (changes['allGroupsOpen'] && !this.autoOpen) {
      this.isGroupOpen = this.allGroupsOpen; // Ouvre ou ferme en fonction de l'état global
      this.emitVisibleCards();
    }
  }

  toggleGroup() {
    this.isGroupOpen = !this.isGroupOpen;
    this.emitVisibleCards();
  }

  loadMore() {
    this.displayedCards += 50;
    this.emitVisibleCards();
  }

  private emitVisibleCards() {
    const indexToLoad: number = this.displayedCards - 50; // Index de la première carte à charger
    const visibleCards = this.cards.slice(indexToLoad, this.displayedCards); // Cartes actuellement visibles
    if (this.isGroupOpen) {
      this.visibleCardsChange.emit(visibleCards);
    }
  }
}
