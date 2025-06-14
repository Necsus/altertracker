import { CommonModule, Location } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CardModel } from '../../01_models/03_business/card.model';
import { CardService } from '../../03_business/card.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';
import { SearchFormService } from './search-form.service';

@Component({
  selector: 'app-search-panel',
  templateUrl: './search-panel.component.html',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule]
})
export class SearchPanelComponent implements OnInit {
  @Output() cardsRetrieved = new EventEmitter<{ cards: CardModel[], searchOffers: boolean }>();
  @Input() showFull: boolean = false;
  searchForm!: FormGroup;
  areFiltersOpen: boolean = true; // État initial des filtres
  areEffectsOpen: boolean = false; // État initial des effets
  areOffersOpen: boolean = false; // État initial des effets
  popoverIndex: number | null = null;
  isLoggedIn = false;
  selectedFactions: string[] = []; // Liste des factions sélectionnées
  selectedRarity: string[] = []; // Liste des factions sélectionnées
  constructor(
    private fb: FormBuilder,
    private loaderService: LoaderService,
    private cardService: CardService,
    private route: ActivatedRoute,
    private authViewService: AuthViewService,
    private router: Router,
    private translate: TranslateService,
    private location: Location,
    private searchFormService: SearchFormService
  ) { }

  ngOnInit() {
    if (this.showFull) {
      this.areFiltersOpen = true;
      this.areEffectsOpen = true;
      this.areOffersOpen = true;
    }
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
      exclude_effect: [''],
      main_cost_range: [''],
      recall_cost_range: [''],
      forest_power_range: [''],
      mountain_power_range: [''],
      ocean_power_range: [''],
      no_condition: [''],
      in_market: [''],
      price_range: ['']
    });

    this.searchFormService.formState$.subscribe(state => {
      if (state) {
        this.searchForm.patchValue(state);
        if (state['faction']) {
          this.selectedFactions = state['faction'].split(',').map((faction: string) => faction.trim());
        }
        if (state['rarity']) {
          this.selectedRarity = state['rarity'].split(',').map((rarity: string) => rarity.trim());
        }
        if (state['in_market'] || state['price_range']) {
          this.areOffersOpen = true; // Ouvre les offres si in_market est défini
        }
        else {
          this.areOffersOpen = false; // Ouvre les filtres si aucun critère n'est défini
        }
        if (state['main_effect'] || state['main_effect_2'] || state['echo_effect'] || state['exclude_effect']) {
          this.areEffectsOpen = true; // Ouvre les offres si in_market est défini
        }
        else {
          this.areEffectsOpen = false; // Ouvre les filtres si aucun critère n'est défini
        }
        if (state['name'] || state['rarity'] || state['faction'] || state['set'] || state['main_cost_range'] || state['recall_cost_range'] ||
          state['forest_power_range'] || state['mountain_power_range'] || state['ocean_power_range']) {
          this.areFiltersOpen = true; // Ouvre les offres si in_market est défini
        } else {
          this.areFiltersOpen = false; // Ouvre les filtres si aucun critère n'est défini
        }
      }
    });

    this.route.queryParams.subscribe((queryParams) => {
      if (Object.keys(queryParams).length === 0) {
        localStorage.removeItem('lastSearchUrl');
      } else {
        this.searchForm.patchValue({
          name: queryParams['name'] || '',
          rarity: queryParams['rarity'] || '',
          faction: queryParams['faction'] || '',
          set: queryParams['set'] || '',
          main_effect: queryParams['main_effect'] || '',
          main_effect_2: queryParams['main_effect_2'] || '',
          echo_effect: queryParams['echo_effect'] || '',
          exclude_effect: queryParams['exclude_effect'] || '',
          main_cost_range: queryParams['main_cost_range'] || '',
          recall_cost_range: queryParams['recall_cost_range'] || '',
          forest_power_range: queryParams['forest_power_range'] || '',
          mountain_power_range: queryParams['mountain_power_range'] || '',
          ocean_power_range: queryParams['ocean_power_range'] || '',
          in_market: queryParams['in_market'] || '',
          price_range: queryParams['price_range'] || '',
          no_condition: queryParams['no_condition'] || ''
        });
        if (queryParams['faction']) {
          this.selectedFactions = queryParams['faction'].split(',').map((faction: string) => faction.trim());
        }
        if (queryParams['rarity']) {
          this.selectedRarity = queryParams['rarity'].split(',').map((rarity: string) => rarity.trim());
        }
      }

    });
  }

  toggleFilters(): void {
    this.areFiltersOpen = !this.areFiltersOpen; // Inverse l'état des filtres
  }
  toggleEffects(): void {
    this.areEffectsOpen = !this.areEffectsOpen; // Inverse l'état des filtres
  }
  toggleOffers(): void {
    this.areOffersOpen = !this.areOffersOpen; // Inverse l'état des filtres
  }

  toggleRarity(rarity: string): void {
    const index = this.selectedRarity.indexOf(rarity);
    if (index === -1) {
      // Ajouter la faction si elle n'est pas déjà sélectionnée
      this.selectedRarity.push(rarity);
    } else {
      // Supprimer la faction si elle est déjà sélectionnée
      this.selectedRarity.splice(index, 1);
    }
    this.searchForm.patchValue({
      rarity: this.selectedRarity.join(',') // Met à jour le formulaire avec les raretés sélectionnées
    });
  }

  toggleFaction(faction: string): void {
    const index = this.selectedFactions.indexOf(faction);
    if (index === -1) {
      // Ajouter la faction si elle n'est pas déjà sélectionnée
      this.selectedFactions.push(faction);
    } else {
      // Supprimer la faction si elle est déjà sélectionnée
      this.selectedFactions.splice(index, 1);
    }
    this.searchForm.patchValue({
      faction: this.selectedFactions.join(',') // Met à jour le formulaire avec les raretés sélectionnées
    });
  }

  isFormValid(): boolean {
    const { name, rarity, faction, set, main_effect, main_effect_2, echo_effect, exclude_effect,
      main_cost_range, recall_cost_range, forest_power_range, mountain_power_range, ocean_power_range,
      in_market, price_range, no_condition } = this.searchForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      name || rarity || faction || set || main_effect || main_effect_2 || echo_effect || exclude_effect || main_cost_range || recall_cost_range ||
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
    this.location.replaceState(searchUrl);
    this.searchCards(formValues);
  }

  searchCards(criteria: any): void {
    const formValues = this.cleanFormValues(this.searchForm.value);
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
      exclude_effect: criteria.exclude_effect,
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
        this.searchFormService.setFormState(formValues);
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
