import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject, catchError, delay, map, of, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../../01_models/03_business/card.model';
import { AlteredService } from '../../03_business/altered.service';
import { CardService } from '../../03_business/card.service';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { CardComponent } from '../../search/card/card.component';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-user-alerts',
  templateUrl: './user-alerts.component.html',
  styleUrls: ['./user-alerts.component.css'],
  imports: [CommonModule, FormsModule, CardComponent, TranslateModule]
})
export class UserAlertsComponent implements OnInit, OnDestroy {
  isLoading: boolean = false; // État de chargement
  alerts: CardModel[] = []; // Liste des recherches
  remainingCards: CardModel[] = []; // Cartes restantes à traiter
  queueProcessing = false; // Indique si la file d'attente est en cours de traitement
  private requestQueue: OfferLiveMarketRequest[] = []; // File d'attente des requêtes
  private progressSubject = new BehaviorSubject<number>(0);
  progress$ = this.progressSubject.asObservable();

  filteredAlerts: CardModel[] = []; // Liste filtrée
  searchQuery: string = ''; // Texte de recherche
  selectedFaction: string = ''; // Filtre sélectionné
  showOnlyWithPrice: boolean = false;
  sortBy: string = '';

  Math = Math;
  currentPage: number = 1;
  itemsPerPage: number = 30;
  totalItems: number = 0;
  totalPages: number = 0;
  paginatedAlerts: CardModel[] = [];

  constructor(
    private userService: UserService,
    private toastService: ToastService,
    private alteredService: AlteredService,
    private cardService: CardService,
    private authViewService: AuthViewService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    this.loadUserAlerts();
  }

  onFiltersChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onSortChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  addCardsToQueue(alerts: CardModel[]): void {
    alerts.map((alert) => alert.isProcessing = true);
    this.remainingCards.push(...alerts); // Ajoute les nouvelles cartes à la file d'attente
    if (!this.queueProcessing) {
      this.processQueue(); // Démarre le traitement de la file d'attente si ce n'est pas déjà en cours
    }
  }

  loadUserAlerts(): void {
    this.isLoading = true; // Démarre le chargement
    this.userService.get_user_alerts$().subscribe({
      next: (response: CardModel[]) => {
        this.alerts = response; // Met à jour la liste des recherches
        this.filteredAlerts = [...this.alerts];
        this.applyFilters();
      },
      error: (err: any) => {
        this.isLoading = false; // Arrête le chargement
        this.toastService.show(err.message, 'error', 5000);
      },
      complete: () => {
        this.isLoading = false; // Arrête le chargement
        this.addCardsToQueue(this.alerts); // Ajoute les alertes à la file d'attente
      }
    });
  }

  // Nouvelle méthode pour changer de page
  onPageChange(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updatePaginatedAlerts();
    }
  }

  // Méthode pour aller à la page précédente
  previousPage(): void {
    if (this.currentPage > 1) {
      this.onPageChange(this.currentPage - 1);
    }
  }

  // Méthode pour aller à la page suivante
  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.onPageChange(this.currentPage + 1);
    }
  }

  // Méthode pour obtenir les numéros de pages à afficher
  getPageNumbers(): number[] {
    const maxPagesToShow = 5;
    const pages: number[] = [];

    let startPage = Math.max(1, this.currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(this.totalPages, startPage + maxPagesToShow - 1);

    // Ajuster le début si on est près de la fin
    if (endPage - startPage + 1 < maxPagesToShow) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
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

    const card = this.remainingCards.shift(); // Récupère la première carte de la file d'attente
    if (card) {
      this.alteredService.getMarketOffer$(card)
        .pipe(
          delay(300), // Respecte le délai entre les requêtes
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
  private applyFilters(): void {
    let filtered = [...this.alerts];

    // Filtre par faction
    if (this.selectedFaction) {
      filtered = filtered.filter(card => card.faction === this.selectedFaction);
    }

    // Filtre par recherche
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      filtered = filtered.filter(card =>
        card.name.toLowerCase().includes(query) ||
        card.reference.toLowerCase().includes(query)
      );
    }

    // Filtre cartes avec prix uniquement
    if (this.showOnlyWithPrice) {
      filtered = filtered.filter(card => card.price && card.price > 0);
    }

    // Tri
    if (this.sortBy) {
      filtered = this.sortCards(filtered, this.sortBy);
    }

    this.filteredAlerts = filtered;
    this.totalItems = filtered.length;
    this.totalPages = Math.ceil(this.totalItems / this.itemsPerPage);

    // S'assurer que la page actuelle est valide
    if (this.currentPage > this.totalPages && this.totalPages > 0) {
      this.currentPage = this.totalPages;
    }

    this.updatePaginatedAlerts();
  }

  private updatePaginatedAlerts(): void {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    this.paginatedAlerts = this.filteredAlerts.slice(startIndex, endIndex);
  }

  private sortCards(cards: any[], sortBy: string): any[] {
    switch (sortBy) {
      case 'name_asc':
        return cards.sort((a, b) => a.name.localeCompare(b.name));
      case 'name_desc':
        return cards.sort((a, b) => b.name.localeCompare(a.name));
      case 'price_asc':
        return cards.sort((a, b) => (a.price || 0) - (b.price || 0));
      case 'price_desc':
        return cards.sort((a, b) => (b.price || 0) - (a.price || 0));
      default:
        return cards;
    }
  }
}
