import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CardModel } from '../../01_models/03_business/card.model';
import { CardService } from '../../03_business/card.service';

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
      rarity: [''],
      faction: [''],
      set: [''],
      main_effect: [''],
      echo_effect: [''],
      main_cost: [''],
      recall_cost: [''],
      in_market: [''],
      no_condition: ['']
    });
  }

  isFormValid(): boolean {
    const { name, rarity, faction, set, main_effect, echo_effect, main_cost, recall_cost, in_market, no_condition } = this.searchForm.value;
    return !!(name || rarity || faction || set || main_effect || echo_effect || main_cost || recall_cost || in_market || no_condition); // Vérifie si au moins un champ est rempli
  }

  onSubmit() {
    const formValues = this.cleanFormValues(this.searchForm.value);
    this.searchCards(formValues);
  }

  searchCards(criteria: any): void {
    this.cardService.search_cards$(
      criteria.name, criteria.rarity, criteria.faction,
      criteria.set, criteria.main_effect, criteria.echo_effect,
      criteria.main_cost, criteria.recall_cost, criteria.in_market,
      criteria.no_condition
    ).subscribe({
      next: (data: CardModel[]) => {
        this.cardsRetrieved.emit(data);
      },
      error: (error) => {
        console.error('Error fetching card data:', error);
      }
    });
  }

  private cleanFormValues(values: any): any {
    // Remplace null par une chaîne vide pour chaque champ
    return Object.keys(values).reduce((acc: any, key) => {
      acc[key] = values[key] === null || values[key] === false ? '' : values[key];
      return acc;
    }, {});
  }
}
