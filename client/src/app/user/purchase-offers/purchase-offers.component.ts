
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { CardModel } from '../../01_models/03_business/card.model';
import { PurchaseService } from '../../03_business/purchase.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { CardComponent } from '../../search/card/card.component';

@Component({
  selector: 'app-purchase-offers',
  templateUrl: './purchase-offers.component.html',
  imports: [FormsModule, RouterModule, CardComponent]
})
export class PurchaseOffersComponent implements OnInit {
  isLoading: boolean = false; // État de chargement
  cards: CardModel[] = []; // Liste des recherches

  constructor(
    private purchaseService: PurchaseService,
    private authViewService: AuthViewService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    this.loadUserPurchaseOffers();
  }
  loadUserPurchaseOffers(): void {
    this.isLoading = true;
    this.purchaseService.getUserPurchases$().subscribe({
      next: (response: CardModel[]) => {
        this.cards = response; // Met à jour la liste des offres d'achat
        this.isLoading = false; // Arrête le chargement
      },
      error: (err: any) => {
        this.isLoading = false; // Arrête le chargement
      },
    });
  }
}
