import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject, catchError, delay, map, of, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { AlteredService } from '../03_business/altered.service';
import { CardService } from '../03_business/card.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { LoaderService } from '../shared/services/loader/loader.service';
import { ToastService } from '../shared/services/toast/toast.service';
import { CardGroupComponent } from './card-group/card-group.component';
import { SaveSearchComponent } from './save-search/save-search.component';
import { SearchPanelComponent } from './search-panel/search-panel.component';

@Component({
  selector: 'app-cards',
  templateUrl: './cards.component.html',
  styleUrls: ['./cards.component.css'],
  imports: [CommonModule, SearchPanelComponent, CardGroupComponent, SaveSearchComponent, TranslateModule]
})
export class CardsComponent implements OnInit, OnDestroy {
  @ViewChild('sidebar') sidebar!: ElementRef;
  sidebarOpen: boolean = true;
  cards: CardModel[] = [];
  groupedCards: { [key: string]: CardModel[] } = {};
  nbCards: number = 0;
  nbCardsInMarket: number = 0;
  autoOpenGroup: string | null = null;
  searchOffers: boolean = false;
  isLoggedIn = false;
  allGroupsOpen: boolean = false;
  remainingCards: CardModel[] = []; // Cartes restantes à traiter
  queueProcessing = false;
  private requestQueue: OfferLiveMarketRequest[] = [];
  private progressSubject = new BehaviorSubject<number>(0);
  progress$ = this.progressSubject.asObservable();

  constructor(
    private cardService: CardService,
    private router: Router,
    private authViewService: AuthViewService,
    private alteredService: AlteredService,
    private loaderService: LoaderService,
    private toastService: ToastService) { }

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

  toggleFilterSlider(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  toggleAllGroups(): void {
    // Ouvre tous les groupes
    this.allGroupsOpen = !this.allGroupsOpen;
  }
  onVisibleCardsChange(visibleCards: CardModel[]): void {
    // Exécute les requêtes pour les cartes visibles
    if (this.isLoggedIn) {
      this.addCardsToQueue(visibleCards);
    } else {
      this.router.navigate(['/login']);
    }
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

  addCardsToQueue(cards: CardModel[]): void {
    cards.map((card) => card.isProcessing = true);
    this.remainingCards.push(...cards); // Ajoute les nouvelles cartes à la file d'attente
    if (!this.queueProcessing) {
      this.processQueue(); // Démarre le traitement de la file d'attente si ce n'est pas déjà en cours
    }
  }

  private processQueue(): void {
    if (this.remainingCards.length === 0) {
      this.progressSubject.next(0); // Réinitialise la progression si la file d'attente est vide
      this.queueProcessing = false; // Arrête le traitement si la file est vide
      // Si la file d'attente des requêtes contient des éléments, les envoyer
      if (this.requestQueue.length > 0) {
        this.flushRequestQueue();
      }
      return;
    }

    this.queueProcessing = true; // Indique que le traitement de la file d'attente est en cours

    const card = this.remainingCards.shift(); // Récupère la première carte de la file d'attente
    if (card) {
      this.alteredService.getMarketOffer$(card)
        .pipe(
          delay(750), // Respecte le délai entre les requêtes
          map((offerRequest) => {
            this.requestQueue.push(offerRequest); // Ajoute la requête à la file d'attente
            this.progressSubject.next(this.requestQueue.length); // Met à jour la progression
            if (this.requestQueue.length >= 10) {
              this.flushRequestQueue(); // Enregistre toutes les 10 requêtes
            }
          }),
          catchError((error) => {
            if (error.message === 'Token invalide ou expiré. Veuillez le réinsérer.') {
              this.handleTokenError(error);
              return of();
            }
            return throwError(() => error);
          })
        )
        .subscribe({
          complete: () => {
            card.isProcessing = false;
            this.processQueue(); // Relance le traitement pour la prochaine carte
          }
        });
    }
  }

  ngOnDestroy(): void {
    this.flushRequestQueue(); // Vide la file d'attente des requêtes
    this.queueProcessing = false; // Arrête le traitement des requêtes
    this.remainingCards = []; // Vide la file d'attente des cartes
  }

  private flushRequestQueue(): void {
    if (this.requestQueue.length > 0) {
      const requestsToSend = [...this.requestQueue];
      this.requestQueue = []; // Vide la file d'attente des requêtes
      this.cardService.post_offer_live_market$(requestsToSend).subscribe({
        next: () => {
          console.log('Mise à jour des offres live market réussie.');
        },
        error: (error) => {
          console.error('Erreur lors de la mise à jour des offres live market :', error);
        }
      });
    }
  }

  private handleTokenError(error: any): void {
    console.error('Erreur 401 détectée : Redirection vers la page /token.');
    localStorage.removeItem('altered_token');
    localStorage.removeItem('cgu_altered_token');
    this.loaderService.hide();
    this.toastService.show(error.message, 'error', 5000);
    this.router.navigate(['/token']);
  }
}
