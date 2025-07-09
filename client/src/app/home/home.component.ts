import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferViewModel } from '../01_models/home/offer-view.model';
import { CardService } from '../03_business/card.service';
import { OfferService } from '../03_business/offer.service';
import { UserService } from '../03_business/user.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { CardImgComponent } from '../cards/card/card-img.component';
import { LocalizedValuePipe } from '../shared/pipes/localized-value.pipe';
import { ToDatePipe } from '../shared/pipes/to-date.pipe';
import { ModalService } from '../shared/services/modal/modal.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule, RouterModule, TranslateModule, LocalizedValuePipe, ToDatePipe]
})
export class HomeComponent implements OnInit {
  currentLanguage: string = 'fr';
  isLoggedIn: boolean = false;
  nbCards: number = 0;
  nbCardsInMarket: number = 0;
  newCardsLoading: boolean = false;
  newCardsCount: Number = 0;
  newCards: CardModel[] = [];
  newOffersLoading: boolean = false;
  newOffersCount: Number = 0;
  newOffers: OfferViewModel[] = [];
  deletedOffersLoading: boolean = false;
  deletedOffersCount: Number = 0;
  deletedOffers: OfferViewModel[] = [];
  editedOffersLoading: boolean = false;
  editedOffersCount: Number = 0;
  editedOffers: OfferViewModel[] = [];
  usersCount: Number = 0;

  constructor(
    private cardService: CardService,
    private offerService: OfferService,
    private userService: UserService,
    private toastService: ToastService,
    private modalService: ModalService,
    private authViewService: AuthViewService,
    private translate: TranslateService,
    private router: Router) {
    this.currentLanguage = this.translate.currentLang || 'en'; // Définit la langue par défaut
    this.translate.onLangChange.subscribe((event) => {
      this.currentLanguage = event.lang;
    });
  }
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
    this.newCardsLoading = true;
    this.cardService.get_last_added_cards$().subscribe({
      next: (response: { count: number, cards: CardModel[] }) => {
        this.newCardsCount = response.count;
        this.newCards = response.cards;
      },
      complete: () => this.newCardsLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.newOffersLoading = true;
    this.offerService.get_last_added_offers$().subscribe({
      next: (response: { count: number, offers: OfferViewModel[] }) => {
        this.newOffersCount = response.count;
        this.newOffers = response.offers;
      },
      complete: () => this.newOffersLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.editedOffersLoading = true;
    this.offerService.get_last_edited_offers$().subscribe({
      next: (response: { count: number, offers: OfferViewModel[] }) => {
        this.editedOffersCount = response.count;
        this.editedOffers = response.offers;
      },
      complete: () => this.editedOffersLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.deletedOffersLoading = true;
    this.offerService.get_last_deleted_offers$().subscribe({
      next: (response: { count: number, offers: OfferViewModel[] }) => {
        this.deletedOffersCount = response.count;
        this.deletedOffers = response.offers;
      },
      complete: () => this.deletedOffersLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.userService.count_all_users$().subscribe({
      next: (response: number) => {
        this.usersCount = Number(response);
      },
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
  }
  openModal(card: CardModel): void {
    const currentLanguage = this.translate.currentLang || 'fr';
    this.modalService.open(CardImgComponent, { src: currentLanguage === 'en' ? card.image_path_en : card.imagePath });
  }
  goToStats(reference: string): void {
    this.router.navigate(['/stats', reference]);
  }
}
