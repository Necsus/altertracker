import { CommonModule } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CardModel } from '../../01_models/03_business/card.model';
import { OfferPurchase } from '../../01_models/03_business/offer-purchase.model';
import { PurchaseService } from '../../03_business/purchase.service';
import { ToastService } from '../services/toast/toast.service';

@Component({
  selector: 'app-purchase-offer',
  templateUrl: './purchase-offer.component.html',
  imports: [CommonModule, ReactiveFormsModule]
})
export class PurchaseOfferComponent implements OnInit {
  @Input() model!: { card: CardModel, purchases: OfferPurchase[] | null };
  purchaseForm!: FormGroup;
  constructor(
    private fb: FormBuilder,
    private purchaseService: PurchaseService,
    private toastService: ToastService) { }
  ngOnInit(): void {
    this.purchaseForm = this.fb.group({
      price: [''],
      currency: ['EUR']
    });
  }
  isFormValid(): boolean {
    const { price, currency } = this.purchaseForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      price && price > 0 && currency
    );
  }
  onSubmit(): void {
    if (this.isFormValid()) {
      const { price, currency } = this.purchaseForm.value;
      const request = {
        reference_card: this.model.card.reference,
        price: price,
        currency: currency
      };

      this.purchaseService.postNewPurchase$(request).subscribe({
        next: (purchase) => {
          // Ajouter l'achat à la liste des achats de la carte
          if (!this.model.purchases) {
            this.model.purchases = [];
          }
          this.model.purchases.push(purchase);
          this.purchaseForm.reset();
          // Afficher un message de succès
          this.toastService.show(`Offre d'achat ajoutée avec succès : ${this.model.card.name} ${purchase.price} ${purchase.currency}`, 'success', 5000);
        }
      });
    }
  }
}
