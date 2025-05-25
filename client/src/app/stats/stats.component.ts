import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferPurchase } from '../01_models/03_business/offer-purchase.model';
import { OfferModel } from '../01_models/03_business/offer.model';
import { UserAlertModel } from '../01_models/03_business/user-alert.model';
import { AlteredService } from '../03_business/altered.service';
import { CardService } from '../03_business/card.service';
import { UserService } from '../03_business/user.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { PurchaseOfferComponent } from '../shared/purchase-offer/purchase-offer.component';
import { ModalService } from '../shared/services/modal/modal.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Component({
  selector: 'app-stats',
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.css'],
  imports: [CommonModule, ReactiveFormsModule]
})
export class StatsComponent implements OnInit {
  reference: string | null = null;
  isLoggedIn: boolean = false;
  searchForm!: FormGroup;
  card!: CardModel | null;
  offers!: OfferModel[] | null;
  purchases!: OfferPurchase[] | null; // Ajouté pour les achats
  is_favorite: boolean = false; // État favori de la carte

  constructor(
    private route: ActivatedRoute,
    private authViewService: AuthViewService,
    private fb: FormBuilder,
    private cardService: CardService,
    private router: Router,
    private userService: UserService,
    private toastService: ToastService,
    private modalService: ModalService,
    private alteredService: AlteredService
  ) { }
  get availableInMarket(): boolean {
    if (this.offers && this.offers.length > 0) {
      return this.offers[0].is_deleted === false;
    }
    return false;
  }
  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
    this.reference = this.route.snapshot.paramMap.get('reference');
    this.searchForm = this.fb.group({
      reference: [this.reference || ''],
    });
    if (this.reference) {
      this.loadCardStats(this.reference);
    }
    // Scroll to top when route changes
    this.router.events.subscribe(() => {
      window.scrollTo(0, 0);
    });
  }

  isFormValid(): boolean {
    const { reference } = this.searchForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      reference
    );
  }

  onSubmit(): void {
    const reference = this.searchForm.get('reference')?.value;
    this.reference = reference;
    if (this.reference) {
      this.loadCardStats(this.reference);
    }
  }

  loadCardStats(reference: string): void {
    this.cardService.get_card_stats$(reference).subscribe({
      next: (response: { card: CardModel, offers: OfferModel[], purchases: OfferPurchase[] }) => {
        this.card = response.card;
        this.is_favorite = !!this.card.alert_id;
        this.offers = response.offers;
        this.purchases = response.purchases;
        this.refreshCardFromAltered();
        this.router.navigate(['/stats', reference]);
      },
      error: (err: any) => {
        console.error(err);
        this.card = null;
        this.offers = null;
      }
    });
  }

  toggleFavorite(): void {
    this.saveFavoriteState();
  }

  saveFavoriteState(): void {
    if (this.card) {
      const reference = this.card.reference;
      const alert_id = this.card.alert_id;
      if (!this.is_favorite && !alert_id) {
        const request = <UserAlertModel>{
          reference_card: reference,
          mail_active: false
        };
        this.userService.post_user_alert$(request).subscribe({
          next: (response: UserAlertModel) => {
            if (this.card) {
              this.is_favorite = !this.is_favorite;
              this.card.alert_id = response.id; // Inverse l'état de la carte
              this.toastService.show(`${reference} ajoutée aux favoris`, 'success', 5000);
            }
          },
          error: (err: any) => {
            this.toastService.show(err.message, 'error', 5000);
          }
        });
      } else {
        if (alert_id) {
          this.userService.delete_user_alert$(alert_id).subscribe({
            next: () => {
              if (this.card) {
                this.is_favorite = !this.is_favorite;
                this.card.alert_id = undefined;
                this.toastService.show(`${reference} supprimée des favoris`, 'success', 5000);
              }
            },
            error: (err: any) => {
              this.toastService.show(err.message, 'error', 5000);
            }
          });
        }
      }
    }
  }

  openPurchaseOfferModal(): void {
    if (this.isLoggedIn) {
      if (this.card) {
        this.modalService.open(PurchaseOfferComponent, { model: { card: this.card, purchases: this.purchases } });
      } else {
        this.toastService.show('Aucune carte sélectionnée', 'warning', 5000);
      }
    } else {
      this.toastService.show('Veuillez vous connecter pour déposer une offre d\'achat', 'warning', 5000);
    }
  }
  refreshCardFromAltered(): void {
    const alteredToken = sessionStorage.getItem('altered_token');
    if (alteredToken && this.card) {
      let offerLiveMarket: OfferLiveMarketRequest;
      this.alteredService.getMarketOffer$(this.card, alteredToken).subscribe({
        next: (offer: OfferLiveMarketRequest) => {
          offerLiveMarket = offer;
        },
        complete: () => {
          if (this.card) {
            this.alteredService.getEnglishCardByReference$(this.card).subscribe({
              complete: () => {
                if (this.card) {
                  this.cardService.updateCard$(this.card, offerLiveMarket).subscribe({
                    next: (response: any) => {
                      console.log(response);
                    }
                  });
                }
              }
            });
          }
        }
      });
    }
  }
}

