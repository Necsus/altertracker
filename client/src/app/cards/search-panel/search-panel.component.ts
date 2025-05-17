import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { CardModel } from '../../01_models/03_business/card.model';
import { CardService } from '../../03_business/card.service';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-search-panel',
  templateUrl: './search-panel.component.html',
  imports: [CommonModule, ReactiveFormsModule]
})
export class SearchPanelComponent implements OnInit {
  @Output() cardsRetrieved = new EventEmitter<{ cards: CardModel[], searchOffers: boolean, fullSearchLiveMarket: boolean }>();
  searchForm!: FormGroup;
  fullSearchLiveMarketLimit: number = 300;
  constructor(
    private fb: FormBuilder,
    private loaderService: LoaderService,
    private cardService: CardService,
    private toastService: ToastService,
    private route: ActivatedRoute
  ) { }

  ngOnInit() {
    this.searchForm = this.fb.group({
      name: [''],
      rarity: [''],
      faction: [''],
      set: [''],
      main_effect: [''],
      main_effect_2: [''],
      echo_effect: [''],
      main_cost: [''],
      recall_cost: [''],
      forest_power: [''],
      mountain_power: [''],
      ocean_power: [''],
      in_market: [''],
      no_condition: [''],
      search_offers: [sessionStorage.getItem('altered_token') ? true : false]
    });

    this.route.queryParams.subscribe((queryParams) => {
      if (Object.keys(queryParams).length === 0) {
        sessionStorage.removeItem('lastSearchUrl');
      }
      this.searchForm.patchValue({
        name: queryParams['name'] || '',
        rarity: queryParams['rarity'] || '',
        faction: queryParams['faction'] || '',
        set: queryParams['set'] || '',
        main_effect: queryParams['main_effect'] || '',
        main_effect_2: queryParams['main_effect_2'] || '',
        echo_effect: queryParams['echo_effect'] || '',
        main_cost: queryParams['main_cost'] || '',
        recall_cost: queryParams['recall_cost'] || '',
        forest_power: queryParams['forest_power'] || '',
        mountain_power: queryParams['mountain_power'] || '',
        ocean_power: queryParams['ocean_power'] || '',
        in_market: queryParams['in_market'] || '',
        no_condition: queryParams['no_condition'] || ''
      });
    });
  }

  isFormValid(): boolean {
    const { name, rarity, faction, set, main_effect, main_effect_2, echo_effect, main_cost, recall_cost, forest_power, mountain_power, ocean_power, in_market, no_condition } = this.searchForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      name || rarity || faction || set || main_effect || main_effect_2 || echo_effect || main_cost || recall_cost ||
      forest_power !== '' && forest_power !== null && forest_power !== undefined ||
      mountain_power !== '' && mountain_power !== null && mountain_power !== undefined ||
      ocean_power !== '' && ocean_power !== null && ocean_power !== undefined ||
      in_market || no_condition
    );
  }

  onSubmit(fullSearchLiveMarket: boolean = false) {
    const formValues = this.cleanFormValues(this.searchForm.value);

    // Construire l'URL avec les paramètres du formulaire
    const queryParams = new URLSearchParams();
    Object.keys(formValues).forEach(key => {
      if (formValues[key] !== null && formValues[key] !== undefined && formValues[key] !== '') {
        queryParams.append(key, formValues[key]);
      }
    });

    // Sauvegarder l'URL dans le sessionStorage
    const searchUrl = `/cards?${queryParams.toString()}`;
    sessionStorage.setItem('lastSearchUrl', searchUrl);

    this.searchCards(formValues, fullSearchLiveMarket);
  }

  searchCards(criteria: any, fullSearchLiveMarket: boolean): void {
    let searchObservable = this.cardService.search_cards$(
      criteria.name, criteria.rarity, criteria.faction,
      criteria.set, criteria.main_effect, criteria.main_effect_2, criteria.echo_effect,
      criteria.main_cost, criteria.recall_cost, criteria.forest_power, criteria.mountain_power,
      criteria.ocean_power, criteria.in_market, criteria.no_condition
    );

    // Appliquer conditionnellement le pipe `withLoader`
    if (!fullSearchLiveMarket) {
      searchObservable = searchObservable.pipe(withLoader(this.loaderService));
    } else {
      this.loaderService.show();
    }

    searchObservable.subscribe({
      next: (data: CardModel[]) => {
        if (fullSearchLiveMarket && data.length > this.fullSearchLiveMarketLimit) {
          this.toastService.show(`Jeu de resultat > ${this.fullSearchLiveMarketLimit}, fullSearchLiveMarket désactivé`, 'warning', 5000);
          this.loaderService.hide();
        } else {
          if (fullSearchLiveMarket && data.length <= 0) {
            this.toastService.show('Pas de résultat', 'warning', 5000);
            this.loaderService.hide();
          } else {
            this.cardsRetrieved.emit({ cards: data, searchOffers: criteria.search_offers, fullSearchLiveMarket: fullSearchLiveMarket });
          }
        }
      },
      error: (error) => {
        console.error('Error fetching card data:', error);
      }
    });
  }

  private cleanFormValues(values: any): any {
    // Conserve les valeurs 0 et remplace uniquement null ou false par une chaîne vide
    return Object.keys(values).reduce((acc: any, key) => {
      if (key === 'forest_power' || key === 'mountain_power' || key === 'ocean_power') {
        acc[key] = values[key]; // Conserve la valeur telle quelle, y compris 0
      } else {
        acc[key] = values[key] === null || values[key] === false ? '' : values[key];
      }
      return acc;
    }, {});
  }
}
