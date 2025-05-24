import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { OfferPurchase } from '../../01_models/03_business/offer-purchase.model';
import { AlteredService } from '../../03_business/altered.service';
import { CardService } from '../../03_business/card.service';
import { PurchaseService } from '../../03_business/purchase.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-purchase-offers',
  templateUrl: './purchase-offers.component.html',
  imports: [CommonModule, FormsModule, RouterModule]
})
export class PurchaseOffersComponent implements OnInit {
  isLoading: boolean = false; // État de chargement
  offers: OfferPurchase[] = []; // Liste des recherches

  constructor(
    private purchaseService: PurchaseService,
    private toastService: ToastService,
    private alteredService: AlteredService,
    private cardService: CardService,
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
      next: (response: OfferPurchase[]) => {
        this.offers = response; // Met à jour la liste des offres d'achat
        this.isLoading = false; // Arrête le chargement
      },
      error: (err: any) => {
        this.isLoading = false; // Arrête le chargement
      },
    });
  }
  deletePurchaseOffer(purchase: OfferPurchase): void {
    this.purchaseService.deletePurchase$(purchase.id).subscribe({
      next: () => {
        this.offers = this.offers.filter((offer: OfferPurchase) => offer.id !== purchase.id);
      },
      error: (err: any) => {
        this.toastService.show(err.message, 'error', 5000);
      }
    });
  }
}
