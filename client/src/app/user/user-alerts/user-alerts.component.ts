import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, from, map, mergeMap, of, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../../01_models/02_api/card/offer-live-market-request.model';
import { UserAlertModel } from '../../01_models/03_business/user-alert.model';
import { AlteredService } from '../../03_business/altered.service';
import { CardService } from '../../03_business/card.service';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { CardComponent } from '../../cards/card/card.component';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-user-alerts',
  templateUrl: './user-alerts.component.html',
  styleUrls: ['./user-alerts.component.css'],
  imports: [CommonModule, CardComponent]
})
export class UserAlertsComponent implements OnInit {
  isLoading: boolean = false; // État de chargement
  alerts: UserAlertModel[] = []; // Liste des recherches

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

  loadUserAlerts(): void {
    this.isLoading = true; // Démarre le chargement
    this.userService.get_user_alerts$().subscribe({
      next: (response: UserAlertModel[]) => {
        this.alerts = response; // Met à jour la liste des recherches
        this.alerts.map((alert: UserAlertModel) => {
          alert.card.alert_id = alert.id; // Associe l'ID de l'alerte à la carte
        });
      },
      error: (err: any) => {
        this.isLoading = false; // Arrête le chargement
        this.toastService.show(err.message, 'error', 5000);
      },
      complete: () => {
        this.isLoading = false; // Arrête le chargement
        const alteredToken = sessionStorage.getItem('altered_token');
        if (alteredToken) {
          const maxConcurrentRequests = 5; // Limite de requêtes simultanées
          const updatedCards: OfferLiveMarketRequest[] = [];
          from(this.alerts)
            .pipe(
              mergeMap(
                (alert) => this.alteredService.getMarketOffer$(alert.card, alteredToken),
                maxConcurrentRequests
              ),
              map((offerRequest) => {
                updatedCards.push(offerRequest);
              }),
              catchError((error) => {
                if (error.message === 'Token invalide ou expiré. Veuillez le réinsérer.') {
                  return of(); // Arrête la propagation des requêtes
                }
                return throwError(() => error);
              })
            )
            .subscribe({
              next: () => { },
              complete: () => {
                // Appeler post_offer_live_market$ avec les cartes mises à jour
                if (updatedCards.length > 0) {
                  this.cardService.post_offer_live_market$(updatedCards).subscribe({
                    next: () => { },
                    error: () => { },
                    complete: () => { }
                  });
                }
              }
            });
        }
      }
    });
  }
}