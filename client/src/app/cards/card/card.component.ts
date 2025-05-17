import { Component, Input } from '@angular/core';
import { CardModel } from '../../01_models/03_business/card.model';
import { UserAlertModel } from '../../01_models/03_business/user-alert.model';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ModalService } from '../../shared/services/modal/modal.service';
import { ToastService } from '../../shared/services/toast/toast.service';
import { CardImgComponent } from './card-img.component';

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html'
})
export class CardComponent {
  @Input() card!: CardModel; // Données de la carte
  isLoggedIn = false;
  is_favorite: boolean = false; // État favori de la carte

  constructor(
    private modalService: ModalService,
    private userService: UserService,
    private toastService: ToastService,
    private authViewService: AuthViewService
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
      if (status) {
        this.is_favorite = !!this.card.alert_id; // Initialiser l'état favori de la carte
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
    this.modalService.open(CardImgComponent, { src: this.card.imagePath });
  }
}
