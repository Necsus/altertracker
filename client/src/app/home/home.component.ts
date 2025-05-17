import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferViewModel } from '../01_models/home/home-view.model';
import { CardService } from '../03_business/card.service';
import { OfferService } from '../03_business/offer.service';
import { CardImgComponent } from '../cards/card/card-img.component';
import { ModalService } from '../shared/services/modal/modal.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule]
})
export class HomeComponent implements OnInit {
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

  constructor(
    private cardService: CardService,
    private offerService: OfferService,
    private toastService: ToastService,
    private modalService: ModalService) { }
  ngOnInit(): void {
    // this.router.navigate(['/cards']);
    this.newCardsLoading = true;
    this.cardService.get_last_added_cards$().subscribe({
      next: (response: CardModel[]) => {
        this.newCardsCount = response.length;
        this.newCards = response.slice(0, 20);
      },
      complete: () => this.newCardsLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.newOffersLoading = true;
    this.offerService.get_last_added_offers$().subscribe({
      next: (response: OfferViewModel[]) => {
        this.newOffersCount = response.length;
        this.newOffers = response.slice(0, 20);
      },
      complete: () => this.newOffersLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.editedOffersLoading = true;
    this.offerService.get_last_edited_offers$().subscribe({
      next: (response: OfferViewModel[]) => {
        this.editedOffersCount = response.length;
        this.editedOffers = response.slice(0, 20);
      },
      complete: () => this.editedOffersLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
    this.deletedOffersLoading = true;
    this.offerService.get_last_deleted_offers$().subscribe({
      next: (response: OfferViewModel[]) => {
        this.deletedOffersCount = response.length;
        this.deletedOffers = response.slice(0, 20);
      },
      complete: () => this.deletedOffersLoading = false,
      error: (err: any) => this.toastService.show(err.message, 'error', 5000)
    });
  }
  openModal(imagePath: string): void {
    this.modalService.open(CardImgComponent, { src: imagePath });
  }
}
