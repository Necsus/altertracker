import { CommonModule } from '@angular/common';
import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CardModel } from '../../01_models/03_business/card.model';
import { CardService } from '../../03_business/card.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';

@Component({
  selector: 'app-old-search-panel',
  templateUrl: './old-search-panel.component.html',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule]
})
export class OldSearchPanelComponent implements OnInit {
  @Output() cardsRetrieved = new EventEmitter<{ cards: CardModel[], searchOffers: boolean }>();
  searchForm!: FormGroup;
  popoverIndex: number | null = null;
  isLoggedIn = false;
  constructor(
    private fb: FormBuilder,
    private loaderService: LoaderService,
    private cardService: CardService,
    private route: ActivatedRoute,
    private authViewService: AuthViewService,
    private router: Router,
    private translate: TranslateService
  ) { }

  ngOnInit() {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
    this.searchForm = this.fb.group({
      name: [''],
      rarity: [''],
      faction: [''],
      set: [''],
      main_effect: [''],
      main_effect_2: [''],
      echo_effect: [''],
      main_cost_range: [''],
      recall_cost_range: [''],
      forest_power_range: [''],
      mountain_power_range: [''],
      ocean_power_range: [''],
      no_condition: [''],
      in_market: [''],
      price_range: ['']
    });

    this.route.queryParams.subscribe((queryParams) => {
      if (Object.keys(queryParams).length === 0) {
        localStorage.removeItem('lastSearchUrl');
      }
      this.searchForm.patchValue({
        name: queryParams['name'] || '',
        rarity: queryParams['rarity'] || '',
        faction: queryParams['faction'] || '',
        set: queryParams['set'] || '',
        main_effect: queryParams['main_effect'] || '',
        main_effect_2: queryParams['main_effect_2'] || '',
        echo_effect: queryParams['echo_effect'] || '',
        main_cost_range: queryParams['main_cost_range'] || '',
        recall_cost_range: queryParams['recall_cost_range'] || '',
        forest_power_range: queryParams['forest_power_range'] || '',
        mountain_power_range: queryParams['mountain_power_range'] || '',
        ocean_power_range: queryParams['ocean_power_range'] || '',
        in_market: queryParams['in_market'] || '',
        price_range: queryParams['price_range'] || '',
        no_condition: queryParams['no_condition'] || ''
      });
    });
  }

  isFormValid(): boolean {
    const { name, rarity, faction, set, main_effect, main_effect_2, echo_effect,
      main_cost_range, recall_cost_range, forest_power_range, mountain_power_range, ocean_power_range,
      in_market, price_range, no_condition } = this.searchForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      name || rarity || faction || set || main_effect || main_effect_2 || echo_effect || main_cost_range || recall_cost_range ||
      forest_power_range !== '' && forest_power_range !== null && forest_power_range !== undefined ||
      mountain_power_range !== '' && mountain_power_range !== null && mountain_power_range !== undefined ||
      ocean_power_range !== '' && ocean_power_range !== null && ocean_power_range !== undefined ||
      price_range !== '' && price_range !== null && price_range !== undefined ||
      in_market || no_condition
    );
  }

  onSubmit() {
    const formValues = this.cleanFormValues(this.searchForm.value);

    // Construire l'URL avec les paramètres du formulaire
    const queryParams = new URLSearchParams();
    Object.keys(formValues).forEach(key => {
      if (formValues[key] !== null && formValues[key] !== undefined && formValues[key] !== '') {
        queryParams.append(key, formValues[key]);
      }
    });

    // Sauvegarder l'URL dans le localStorage
    const searchUrl = `/cards?${queryParams.toString()}`;
    localStorage.setItem('lastSearchUrl', searchUrl);
    this.searchCards(formValues);
  }

  searchCards(criteria: any): void {
    if (criteria.in_market) {
      if (!this.isLoggedIn) {
        this.router.navigate(['/login']);
        return;
      }
    }
    const request = {
      name: criteria.name,
      rarity: criteria.rarity,
      faction: criteria.faction,
      set: criteria.set,
      main_effect: criteria.main_effect,
      main_effect_2: criteria.main_effect_2,
      echo_effect: criteria.echo_effect,
      main_cost_range: this.buildRange(criteria.main_cost_range),
      recall_cost_range: this.buildRange(criteria.recall_cost_range),
      forest_power_range: this.buildRange(criteria.forest_power_range),
      mountain_power_range: this.buildRange(criteria.mountain_power_range),
      ocean_power_range: this.buildRange(criteria.ocean_power_range),
      no_condition: criteria.no_condition,
      in_market: criteria.in_market,
      price_range: this.buildRange(criteria.price_range),
      en: (this.translate.currentLang || 'fr') === 'en' ? true : false
    }
    let searchObservable = this.cardService.search_cards$(request);
    // Appliquer conditionnellement le pipe `withLoader`
    searchObservable = searchObservable.pipe(withLoader(this.loaderService));
    searchObservable.subscribe({
      next: (data: CardModel[]) => {
        this.cardsRetrieved.emit({ cards: data, searchOffers: criteria.in_market });
      },
      error: (error) => {
        console.error('Error fetching card data:', error);
      }
    });
  }

  private cleanFormValues(values: any): any {
    // Conserve les valeurs 0 et remplace uniquement null ou false par une chaîne vide
    return Object.keys(values).reduce((acc: any, key) => {
      if (key === 'forest_power_range' || key === 'mountain_power_range' || key === 'ocean_power_range') {
        acc[key] = values[key]; // Conserve la valeur telle quelle, y compris 0
      } else {
        acc[key] = values[key] === null || values[key] === false ? '' : values[key];
      }
      return acc;
    }, {});
  }

  private buildRange(range: string): { min: number, max: number } | null {
    if ((typeof range === 'string' && range.trim() === '') || range === null || range === undefined) {
      return null;
    }

    // Si range est un nombre, définir min et max à cette valeur
    if (typeof range === 'number' || !isNaN(Number(range))) {
      const value = Number(range);
      return { min: value, max: value };
    }

    // Si range est une chaîne, traiter comme une plage
    const parts = range.split('-').map(part => part.trim());
    if (parts.length !== 2) {
      return null; // Format de plage invalide
    }

    const min = parseInt(parts[0], 10);
    const max = parseInt(parts[1], 10);
    if (isNaN(min) || isNaN(max)) {
      return null; // Nombres invalides
    }

    return { min, max };
  }
  showPopover(index: number) {
    this.popoverIndex = index;
  }

  hidePopover() {
    this.popoverIndex = null;
  }
}
