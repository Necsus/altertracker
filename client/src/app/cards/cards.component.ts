import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, from, map, mergeMap, of, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { AlteredService } from '../03_business/altered.service';
import { CardService } from '../03_business/card.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { LoaderService } from '../shared/services/loader/loader.service';
import { CardGroupComponent } from './card-group/card-group.component';
import { SaveSearchComponent } from './save-search/save-search.component';
import { SearchPanelComponent } from './search-panel/search-panel.component';

@Component({
  selector: 'app-cards',
  templateUrl: './cards.component.html',
  imports: [CommonModule, SearchPanelComponent, CardGroupComponent, SaveSearchComponent]
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

  constructor(
    private cardService: CardService,
    private alteredService: AlteredService,
    private router: Router,
    private loaderService: LoaderService,
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

  onVisibleCardsChange(visibleCards: CardModel[]): void {
    // Exécute les requêtes pour les cartes visibles
    if (this.searchOffers) {
      this.getMarketOffer(visibleCards);
    }
  }

  private getMarketOffer(cards: CardModel[]): void {
    const alteredToken = sessionStorage.getItem('altered_token');
    if (alteredToken) {
      const maxConcurrentRequests = 5; // Limite de requêtes simultanées
      const updatedCards: OfferLiveMarketRequest[] = [];
      from(cards)
        .pipe(
          mergeMap(
            (card) => this.alteredService.getMarketOffer$(card, alteredToken),
            maxConcurrentRequests
          ),
          map((offerRequest) => {
            // Ajouter chaque objet OfferLiveMarketRequest à updatedCards
            updatedCards.push(offerRequest);
          }),
          catchError((error) => {
            if (error.message === 'Token invalide ou expiré. Veuillez le réinsérer.') {
              console.error('Erreur 401 détectée : Redirection vers la page /token.');
              sessionStorage.removeItem('altered_token');
              sessionStorage.removeItem('cgu_altered_token');
              this.loaderService.hide();
              this.router.navigate(['/token']); // Redirige l'utilisateur vers la page /token
              return of(); // Arrête la propagation des requêtes
            }
            return throwError(() => error);
          })
        )
        .subscribe({
          next: () => { },
          error: (error) => {
            console.error('Erreur lors de la récupération des offres :', error);
          },
          complete: () => {
            console.log('Toutes les offres visibles ont été récupérées.');
            // Appeler post_offer_live_market$ avec les cartes mises à jour
            if (updatedCards.length > 0) {
              this.cardService.post_offer_live_market$(updatedCards).subscribe({
                next: () => {
                  console.log('Mise à jour des offres live market réussie.');
                },
                error: (error) => {
                  console.error('Erreur lors de la mise à jour des offres live market :', error);
                },
                complete: () => { }
              });
            }
          }
        });
    } else {
      this.router.navigate(['/token']);
    }
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
