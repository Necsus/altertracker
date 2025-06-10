import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject, catchError, delay, map, of, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../../01_models/02_api/card/offer-live-market-request.model';
import { UserCollectionModel } from '../../01_models/03_business/user-collection.model';
import { AlteredService } from '../../03_business/altered.service';
import { CardService } from '../../03_business/card.service';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { CardComponent } from '../../cards/card/card.component';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';

@Component({
  selector: 'app-collection',
  templateUrl: './collection.component.html',
  styleUrls: ['./collection.component.css'],
  imports: [CommonModule, FormsModule, RouterModule, CardComponent, TranslateModule]
})
export class CollectionComponent implements OnInit, OnDestroy {
  cards!: UserCollectionModel[]; // Remplacez any par le type approprié pour vos cartes
  remainingCards: UserCollectionModel[] = []; // Cartes restantes à traiter
  queueProcessing = false; // Indique si la file d'attente est en cours de traitement
  private requestQueue: OfferLiveMarketRequest[] = []; // File d'attente des requêtes
  private progressSubject = new BehaviorSubject<number>(0);
  progress$ = this.progressSubject.asObservable();

  filteredCollection: UserCollectionModel[] = []; // Liste filtrée
  searchQuery: string = ''; // Texte de recherche
  selectedFaction: string = ''; // Filtre sélectionné

  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private alteredService: AlteredService,
    private userService: UserService,
    private loaderService: LoaderService,
    private cardService: CardService
  ) {
  }
  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    this.getUserCollection();
  }

  onSearchChange(): void {
    this.filterCollection();
  }


  onFactionChange(): void {
    this.filterCollection();
  }


  filterCollection(): void {
    this.filteredCollection = this.cards.filter(collection => {
      const matchesSearch = collection.card.name.toLowerCase().includes(this.searchQuery.toLowerCase());
      const matchesFaction = collection.card.faction.includes(this.selectedFaction);
      return matchesSearch && matchesFaction;
    });
  }

  getUserCollection(): void {
    this.userService.get_user_collection$().subscribe({
      next: (response: UserCollectionModel[]) => {
        this.cards = response;
        this.filteredCollection = [...response]; // Initialiser la collection filtrée
        this.addCardsToQueue(this.cards); // Ajoute les cartes à la file d'attente
      }
    });
  }

  importCollection(): void {
    const alteredToken = localStorage.getItem('altered_token');
    if (!alteredToken) {
      this.router.navigate(['/token'], { queryParams: { callback: 'collection' } });
      return;
    }
    let page = 1;
    const allCards: string[] = []; // Stocker toutes les références de cartes

    const fetchPage = () => {
      this.alteredService.getCollection$(alteredToken, page)
        .pipe(withLoader(this.loaderService))
        .subscribe({
          next: (response) => {
            // Ajouter les références de cartes à la liste
            allCards.push(...response['hydra:member'].map((card: any) => card['reference']));

            // Vérifier s'il reste des éléments à récupérer
            if (response['hydra:totalItems'] > allCards.length) {
              page++; // Passer à la page suivante
              fetchPage(); // Récursivité pour récupérer la page suivante
            } else {
              const request = {
                collection: allCards
              };
              localStorage.removeItem('altered_token'); // Supprimer le token après l'importation
              localStorage.removeItem('cgu_altered_token'); // Supprimer le token CGU après l'importation
              this.userService.post_user_collection$(request).subscribe({
                next: (response: any) => {
                  this.cards = response; // Mettre à jour les cartes affichées
                },
                complete: () => {
                  this.addCardsToQueue(this.cards); // Ajouter les cartes à la file d'attente
                }
              });
            }
          },
          error: (error) => {
            if (error.message === 'Token invalide ou expiré. Veuillez le réinsérer.') {
              console.error('Erreur 401 détectée : Redirection vers la page /token.');
              localStorage.removeItem('altered_token');
              localStorage.removeItem('cgu_altered_token');
              this.router.navigate(['/token'], { queryParams: { callback: 'collection' } });
            }
          }
        });
    };

    // Démarrer la récupération avec la première page
    fetchPage();
  }

  addCardsToQueue(collections: UserCollectionModel[]): void {
    collections.map((collection) => collection.card.isProcessing = true);
    this.remainingCards.push(...collections); // Ajoute les nouvelles cartes à la file d'attente
    if (!this.queueProcessing) {
      this.processQueue(); // Démarre le traitement de la file d'attente si ce n'est pas déjà en cours
    }
  }

  ngOnDestroy(): void {
    this.flushRequestQueue(); // Vide la file d'attente des requêtes
    this.queueProcessing = false; // Arrête le traitement des requêtes
    this.remainingCards = []; // Vide la file d'attente des cartes
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

    const collection = this.remainingCards.shift(); // Récupère la première carte de la file d'attente
    if (collection) {
      this.alteredService.getMarketOffer$(collection.card)
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
            collection.card.isProcessing = false;
            this.processQueue(); // Relance le traitement pour la prochaine carte
          }
        });
    }
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
  }
}
