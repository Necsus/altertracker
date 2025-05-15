import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { DeletedOffer, EditedOffer, NewCard, NewOffer, PurchaseOffer } from '../01_models/home/home-view.model';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule]
})
export class HomeComponent implements OnInit {
  newCards: NewCard[] = [];
  newOffers: NewOffer[] = [];
  deletedOffers: DeletedOffer[] = [];
  editedOffers: EditedOffer[] = [];
  purchaseOffers: PurchaseOffer[] = [];

  constructor(private router: Router) { }
  ngOnInit(): void {
    // this.router.navigate(['/cards']);
  }
}
