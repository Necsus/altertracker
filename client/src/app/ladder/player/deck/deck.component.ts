import { CommonModule } from '@angular/common';
import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { Router } from '@angular/router';
import { DeckModel, DeckService } from '../../../03_business/deck.service';

@Component({
  selector: 'app-player-deck',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './deck.component.html'
})
export class DeckComponent {
  player_id = input.required<string>();
  selectedSeason = input.required<number>();

  private readonly deckService = inject(DeckService);
  private readonly router = inject(Router);

  selectedFaction = signal<string | undefined>(undefined);
  currentPage = signal<number>(1);

  decks = signal<DeckModel[]>([]);
  pagination = signal<any>({
    current_page: 1,
    total_pages: 1,
    total_decks: 0,
    limit: 50
  });

  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);

  // Computed
  availableFactions = computed(() => {
    const factions = new Set(this.decks().map(d => d.faction));
    return Array.from(factions).sort();
  });

  filteredDecks = computed(() => {
    const faction = this.selectedFaction();
    if (!faction) return this.decks();
    return this.decks().filter(d => d.faction === faction);
  });

  constructor() {
    // Effect pour charger les decks quand les paramètres changent
    effect(() => {
      const playerId = this.player_id();
      if (playerId) {
        this.loadDecks();
      }
    });
  }

  loadDecks(): void {
    const playerId = this.player_id();
    if (!playerId) return;

    this.isLoading.set(true);
    this.error.set(null);

    this.deckService.get_player_decks$(
      playerId,
      this.selectedSeason(),
      this.selectedFaction(),
      this.currentPage(),
      50
    ).subscribe({
      next: (response) => {
        this.decks.set(response.decks || []);
        this.pagination.set(response.pagination || {
          current_page: 1,
          total_pages: 1,
          total_decks: 0,
          limit: 50
        });
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Error loading decks:', err);
        this.error.set('Erreur lors du chargement des decks');
        this.isLoading.set(false);
      }
    });
  }

  onFactionChange(faction: string): void {
    this.selectedFaction.set(faction || undefined);
    this.currentPage.set(1);
    this.loadDecks();
  }

  goToDeck(deckId: string): void {
    this.router.navigate(['/deck', deckId]);
  }

  goToArchetype(archetypeId: string): void {
    if (archetypeId) {
      this.router.navigate(['/archetype', archetypeId]);
    }
  }

  getFactionImageUrl(faction: string): string {
    return `assets/images/factions/${faction}.webp`;
  }

  getFactionGradient(faction: string): string {
    const gradients: { [key: string]: string } = {
      'AX': 'from-blue-600 to-blue-800',
      'BR': 'from-red-600 to-red-800',
      'LY': 'from-green-600 to-green-800',
      'MU': 'from-purple-600 to-purple-800',
      'OR': 'from-amber-600 to-amber-800',
      'YZ': 'from-teal-600 to-teal-800'
    };
    return gradients[faction] || 'from-gray-600 to-gray-800';
  }

  previousPage(): void {
    if (this.currentPage() > 1) {
      this.currentPage.update(page => page - 1);
      this.loadDecks();
    }
  }

  nextPage(): void {
    if (this.currentPage() < this.pagination().total_pages) {
      this.currentPage.update(page => page + 1);
      this.loadDecks();
    }
  }

  getWinRateColor(winRate: number): string {
    if (winRate >= 60) return 'text-green-400';
    if (winRate >= 50) return 'text-amber-400';
    return 'text-red-400';
  }
}
