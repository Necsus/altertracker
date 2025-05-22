import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferViewModel } from '../01_models/home/offer-view.model';
import { CardService } from '../03_business/card.service';
import { OfferService } from '../03_business/offer.service';
import { UserService } from '../03_business/user.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { CardImgComponent } from '../cards/card/card-img.component';
import { ModalService } from '../shared/services/modal/modal.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule, RouterModule]
})
export class HomeComponent implements OnInit {
  isLoggedIn: boolean = false;
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
  // purchaseOffers: PurchaseOffer[] = [];
  usersCount: Number = 0;

  constructor(
    private cardService: CardService,
    private offerService: OfferService,
    private userService: UserService,
    private toastService: ToastService,
    private modalService: ModalService,
    private authViewService: AuthViewService) { }
  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
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
        this.usersCount = response;
      },
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
  }
  openModal(imagePath: string): void {
    this.modalService.open(CardImgComponent, { src: imagePath });
  }
}
