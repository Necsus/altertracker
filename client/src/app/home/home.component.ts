import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { CardModel } from '../01_models/03_business/card.model';
import { DeletedOffer, EditedOffer, NewOffer, PurchaseOffer } from '../01_models/home/home-view.model';
import { CardService } from '../03_business/card.service';
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
  newOffers: NewOffer[] = [];
  deletedOffers: DeletedOffer[] = [];
  editedOffers: EditedOffer[] = [];
  purchaseOffers: PurchaseOffer[] = [];


  constructor(
    private cardService: CardService,
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
  }
  openModal(imagePath: string): void {
    this.modalService.open(CardImgComponent, { src: imagePath });
  }
}
