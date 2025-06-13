import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { catchError, map, of, throwError } from 'rxjs';
import { CardModel } from '../../01_models/03_business/card.model';
import { OfferPurchase } from '../../01_models/03_business/offer-purchase.model';
import { UserAlertModel } from '../../01_models/03_business/user-alert.model';
import { AlteredService } from '../../03_business/altered.service';
import { CardService } from '../../03_business/card.service';
import { PurchaseService } from '../../03_business/purchase.service';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { LocalizedValuePipe } from '../../shared/pipes/localized-value.pipe';
import { LoaderService } from '../../shared/services/loader/loader.service';
import { ModalService } from '../../shared/services/modal/modal.service';
import { ToastService } from '../../shared/services/toast/toast.service';
import { CardImgComponent } from './card-img.component';

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html',
  styleUrls: ['./card.component.css'],
  imports: [CommonModule, RouterModule, FormsModule, TranslateModule, LocalizedValuePipe],
})
export class CardComponent {
  @Input() card!: CardModel; // Données de la carte
  isLoggedIn = false;
  is_favorite: boolean = false; // État favori de la carte
  isRefreshButtonVisible: boolean = true; // État du bouton Refresh
  constructor(
    private modalService: ModalService,
    private userService: UserService,
    private toastService: ToastService,
    private authViewService: AuthViewService,
    private alteredService: AlteredService,
    private router: Router,
    private loaderService: LoaderService,
    private cardService: CardService,
    private translate: TranslateService,
    private purchaseService: PurchaseService
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
      if (status) {
        this.is_favorite = !!this.card.alert?.id || !!this.card.alert_id; // Initialiser l'état favori de la carte
      }
    });
  }

  toggleFavorite(): void {
    this.saveFavoriteState();
  }

  saveFavoriteState(): void {
    const reference = this.card.reference;
    const alert_id = this.card.alert_id;
    if (!this.is_favorite && !alert_id) {
      const request = <UserAlertModel>{
        reference_card: reference,
        mail_active: false
      };
      this.userService.post_user_alert$(request).subscribe({
        next: (response: UserAlertModel) => {
          this.is_favorite = !this.is_favorite;
          this.card.alert_id = response.id; // Inverse l'état de la carte
          this.toastService.show(`${reference} ajoutée aux favoris`, 'success', 5000);
        },
        error: (err: any) => {
          this.toastService.show(err.message, 'error', 5000);
        }
      });
    } else {
      if (alert_id) {
        this.userService.delete_user_alert$(alert_id).subscribe({
          next: () => {
            this.is_favorite = !this.is_favorite;
            this.card.alert_id = undefined;
            this.toastService.show(`${reference} supprimée des favoris`, 'success', 5000);
          },
          error: (err: any) => {
            this.toastService.show(err.message, 'error', 5000);
          }
        });
      }
    }
  }

  goToOffer(): void {
    if (this.card.url_offer) {
      window.open(this.card.url_offer, '_blank');
    }
  }

  openModal(): void {
    const currentLanguage = this.translate.currentLang || 'fr';
    this.modalService.open(CardImgComponent, { src: currentLanguage === 'en' ? this.card.image_path_en : this.card.imagePath });
  }

  copyToClipboard(reference: string): void {
    navigator.clipboard.writeText(reference).then(() => {
      this.toastService.show('Référence copiée dans le presse-papiers !', 'success', 5000);
    }).catch((error) => {
      console.error('Erreur lors de la copie dans le presse-papiers :', error);
      this.toastService.show('Erreur lors de la copie.', 'error', 5000);
    });
  }

  refreshOffer(): void {
    if (this.card) {
      this.card.isProcessing = true;
      this.alteredService.getMarketOffer$(this.card)
        .pipe(
          map((offerRequest) => {
            let request = [];
            request.push(offerRequest);
            this.cardService.post_offer_live_market$(request).subscribe({
              next: () => {

              },
              error: (error) => {
                console.error('Erreur lors de la mise à jour des offres live market :', error);
              }
            });
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
            this.card.isProcessing = false;
            this.isRefreshButtonVisible = false;
          }
        });
    }
  }
  toggleEmailNotifications(): void {
    if (this.card.alert) {// Inverse l'état des notifications par e-mail
      this.card.alert.mail_active = !this.card.alert.mail_active;
      this.userService.put_user_alert$(this.card.alert).subscribe({
        next: () => { },
        error: (err: any) => {// Rétablit l'état précédent en cas d'erreur
          if (this.card.alert) {
            this.card.alert.mail_active = !this.card.alert.mail_active;
          }
        },
      });
    }
  }
  deletePurchaseOffer(purchase: OfferPurchase): void {
    if (this.card && this.card.mine_purchase_offers) {
      {
        this.purchaseService.deletePurchase$(purchase.id).subscribe({
          next: () => {
            this.card.mine_purchase_offers = this.card.mine_purchase_offers?.filter((offer: OfferPurchase) => offer.id !== purchase.id);
          },
          error: (err: any) => {
            this.toastService.show(err.message, 'error', 5000);
          }
        });
      }
    }
  }
  private handleTokenError(error: any): void {
    console.error('Erreur 401 détectée : Redirection vers la page /token.');
    localStorage.removeItem('altered_token');
    localStorage.removeItem('cgu_altered_token');
    this.loaderService.hide();
  }
}
