import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnDestroy, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CardModel } from '../../01_models/03_business/card.model';
import { CardService } from '../../03_business/card.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';
import { ModalService } from '../../shared/services/modal/modal.service';
import { EffectBuilderComponent } from './effect-builder.component';

@Component({
  selector: 'app-search-panel',
  templateUrl: './search-panel.component.html',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule]
})
export class SearchPanelComponent implements OnInit, OnDestroy {
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
  private routeSubscription: any;
  constructor(
    private fb: FormBuilder,
    private loaderService: LoaderService,
    private cardService: CardService,
    private route: ActivatedRoute,
    private authViewService: AuthViewService,
    private router: Router,
    private translate: TranslateService,
    private modalService: ModalService
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
      subtype: [''],
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
      price_range: [''],
      dataset_type: ['']
    });

    // Patch le formulaire avec les query params actuels dès l'init
    const queryParams = this.route.snapshot.queryParams;
    this.patchFormWithQueryParams(queryParams);

    if (queryParams['dataset_type']) {
      this.onSubmit();
    }

    this.routeSubscription = this.route.queryParams.subscribe((queryParams) => {
      this.patchFormWithQueryParams(queryParams);

      // Ouvre/ferme les sections selon les critères
      this.areOffersOpen = this.showFull || !!(queryParams['in_market'] || queryParams['price_range']);
      this.areEffectsOpen = this.showFull || !!(queryParams['main_effect'] || queryParams['main_effect_2'] || queryParams['echo_effect'] || queryParams['exclude_effect']);
      this.areFiltersOpen = this.showFull || !!(
        queryParams['name'] || queryParams['rarity'] || queryParams['faction'] || queryParams['set'] || queryParams['subtype'] ||
        queryParams['main_cost_range'] || queryParams['recall_cost_range'] ||
        queryParams['forest_power_range'] || queryParams['mountain_power_range'] || queryParams['ocean_power_range']
      );
    });
  }

  patchFormWithQueryParams(queryParams: any): void {
    this.searchForm.patchValue({
      name: queryParams['name'] || '',
      rarity: queryParams['rarity'] || '',
      faction: queryParams['faction'] || '',
      set: queryParams['set'] || '',
      subtype: queryParams['subtype'] || '',
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
      no_condition: queryParams['no_condition'] || '',
      dataset_type: queryParams['dataset_type'] || ''
    }, { emitEvent: false }); // Ne pas déclencher valueChanges ici

    // Synchronise les tableaux pour l'affichage
    this.selectedFactions = (queryParams['faction'] || '').split(',').filter(Boolean);
    this.selectedRarity = (queryParams['rarity'] || '').split(',').filter(Boolean);
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
    const { name, rarity, faction, set, subtype, main_effect, main_effect_2, echo_effect, exclude_effect,
      main_cost_range, recall_cost_range, forest_power_range, mountain_power_range, ocean_power_range,
      in_market, price_range, no_condition, dataset_type } = this.searchForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      name || rarity || faction || set || subtype || main_effect || main_effect_2 || echo_effect || exclude_effect || main_cost_range || recall_cost_range ||
      forest_power_range !== '' && forest_power_range !== null && forest_power_range !== undefined ||
      mountain_power_range !== '' && mountain_power_range !== null && mountain_power_range !== undefined ||
      ocean_power_range !== '' && ocean_power_range !== null && ocean_power_range !== undefined ||
      price_range !== '' && price_range !== null && price_range !== undefined ||
      in_market || no_condition || dataset_type
    );
  }


  onSubmit() {
    const formValues = this.cleanFormValues(this.searchForm.value);
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: formValues,
      queryParamsHandling: 'merge', // merge pour garder les autres params éventuels
      replaceUrl: true
    });
    const queryParams = new URLSearchParams();
    Object.keys(formValues).forEach(key => {
      if (formValues[key] !== null && formValues[key] !== undefined && formValues[key] !== '') {
        queryParams.append(key, formValues[key]);
      }
    });
    // const searchUrl = `/cards?${queryParams.toString()}`;
    // localStorage.setItem('lastSearchUrl', searchUrl);
    this.searchCards(formValues);
  }

  ngOnDestroy() {
    if (this.routeSubscription) {
      this.routeSubscription.unsubscribe();
    }
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
      subtype: criteria.subtype,
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
      en: (this.translate.currentLang || 'fr') === 'en' ? true : false,
      dataset_type: criteria.dataset_type
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

  openEffectBuilder(effectType: 'main_effect' | 'main_effect_2' | 'echo_effect' | 'exclude_effect') {
    const modalRef = this.modalService.open(EffectBuilderComponent);
    // Passe la référence au composant dynamique
    const assignModalRef = () => {
      if (modalRef.instance.componentRef) {
        modalRef.instance.componentRef.instance.modalRef = modalRef;
        return true;
      }
      return false;
    };
    if (!assignModalRef()) {
      // Si non dispo, réessaie rapidement jusqu’à ce que ce soit prêt
      const interval = setInterval(() => {
        if (assignModalRef()) clearInterval(interval);
      }, 10);
    }
    modalRef.onDestroy(() => {
      const result = modalRef.instance.componentRef?.instance.result;
      if (result) {
        this.searchForm.get(effectType)?.setValue(result);
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
