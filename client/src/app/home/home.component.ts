import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CardModel } from '../01_models/03_business/card.model';
import { DeletedOffer, EditedOffer, NewOffer, PurchaseOffer } from '../01_models/home/home-view.model';
import { CardService } from '../03_business/card.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule]
})
export class HomeComponent implements OnInit {
  newCards: CardModel[] = [];
  newOffers: NewOffer[] = [];
  deletedOffers: DeletedOffer[] = [];
  editedOffers: EditedOffer[] = [];
  purchaseOffers: PurchaseOffer[] = [];

  constructor(private router: Router, private cardService: CardService) { }
  ngOnInit(): void {
    // this.router.navigate(['/cards']);
    this.cardService.get_last_added_cards$().subscribe({
      next: (response: CardModel[]) => {
        this.newCards = response;
      }
    })
  }
}
