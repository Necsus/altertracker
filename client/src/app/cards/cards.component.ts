import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject } from 'rxjs';
import { CardModel } from '../01_models/03_business/card.model';
import { CardService } from '../03_business/card.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { CardGroupComponent } from './card-group/card-group.component';
import { SaveSearchComponent } from './save-search/save-search.component';
import { SearchPanelComponent } from './search-panel/search-panel.component';

@Component({
  selector: 'app-cards',
  templateUrl: './cards.component.html',
  styleUrls: ['./cards.component.css'],
  imports: [CommonModule, SearchPanelComponent, CardGroupComponent, SaveSearchComponent, TranslateModule]
})
export class CardsComponent implements OnInit {
  cards: CardModel[] = [];
  groupedCards: { [key: string]: CardModel[] } = {};
  nbCards: number = 0;
  nbCardsInMarket: number = 0;
  autoOpenGroup: string | null = null;
  searchOffers: boolean = false;
  isLoggedIn = false;
  allGroupsOpen: boolean = false;
  remainingCards: CardModel[] = []; // Cartes restantes à traiter
  queueProcessing = false; // Indique si la file d'attente est en cours de traitement
  private progressSubject = new BehaviorSubject<number>(0);
  progress$ = this.progressSubject.asObservable();

  constructor(
    private cardService: CardService,
    private router: Router,
    private authViewService: AuthViewService) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
    this.cardService.count_all_cards$().subscribe({
      next: (count: number) => {
        this.nbCards = count;
      },
      error: (error) => {
        console.error('Error fetching card count:', error);
      }
    });
    this.cardService.count_all_cards_in_market$().subscribe({
      next: (count: number) => {
        this.nbCardsInMarket = count;
      },
      error: (error) => {
        console.error('Error fetching card count:', error);
      }
    });
  }

  toggleAllGroups(): void {
    // Ouvre tous les groupes
    this.allGroupsOpen = !this.allGroupsOpen;
  }

  onCardsRetrieved(event: { cards: CardModel[]; searchOffers: boolean }): void {
    if (this.allGroupsOpen) {
      this.allGroupsOpen = false; // Si tous les groupes sont ouverts, ne pas en ouvrir un automatiquement
    }
    const { cards, searchOffers } = event;
    this.cards = cards;
    this.searchOffers = searchOffers;
    this.groupCardsByName();

    // Détecter un seul groupe
    const groupNames = Object.keys(this.groupedCards);
    this.autoOpenGroup = groupNames.length === 1 ? groupNames[0] : null;
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
