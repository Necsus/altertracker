import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CardModel } from '../../00_models/02_business/card.model';
import { CardService } from '../../02_business/card.service';

@Component({
  selector: 'app-search-panel',
  templateUrl: './search-panel.component.html',
  imports: [CommonModule, ReactiveFormsModule]
})
export class SearchPanelComponent implements OnInit {
  @Output() cardsRetrieved = new EventEmitter<CardModel[]>();
  searchForm!: FormGroup;
  constructor(
    private fb: FormBuilder,
    private cardService: CardService) { }

  ngOnInit() {
    this.searchForm = this.fb.group({
      name: [''],
      effect: [''],
      cost: ['']
    });
  }

  isFormValid(): boolean {
    const { name, effect, cost } = this.searchForm.value;
    return !!(name || effect || cost); // Vérifie si au moins un champ est rempli
  }

  onSubmit() {
    const formValues = this.searchForm.value;
    console.log('Recherche avec :', formValues);
    // Tu peux ensuite appeler ton service ou ta logique ici
    this.searchCards(formValues);
  }

  searchCards(criteria: any): void {
    this.cardService.search_cards$(criteria.name, criteria.effect, criteria.cost).subscribe({
      next: (data: CardModel[]) => {
        this.cardsRetrieved.emit(data);
      },
      error: (error) => {
        console.error('Error fetching card data:', error);
      }
    });
  }
}
