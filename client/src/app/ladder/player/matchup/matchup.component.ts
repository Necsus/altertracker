import { CommonModule } from '@angular/common';
import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { GameModel } from '../../../01_models/03_business/game.model';
import { PlayerService } from '../../../03_business/player.service';

// ✅ Interfaces pour les matchups
interface HeroMatchup {
  hero: string;
  heroFull: string;
  faction: string;
  games: number;
  wins: number;
  losses: number;
  draws: number;
  winRate: number;
}

interface FactionMatchup {
  faction: string;
  games: number;
  wins: number;
  losses: number;
  draws: number;
  winRate: number;
}

@Component({
  selector: 'app-player-matchups',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './matchup.component.html'
})
export class MatchupComponent {
  // ✅ Inputs (signal-based)
  player_id = input.required<string>();
  selectedSeason = input.required<number>();

  // ✅ State
  private readonly playerService = inject(PlayerService);

  // ✅ Transformer games en signal pour la réactivité
  games = signal<GameModel[]>([]);
  isLoading = false;

  // ✅ Signal pour le filtre de héros sélectionné
  selectedPlayerHero = signal<string>('ALL');

  // ✅ Signal pour le filtre de faction sélectionnée
  selectedPlayerFaction = signal<string>('ALL');

  // ✅ Computed: Compte total de games avec héros non null
  readonly totalHeroGames = computed(() => {
    return this.games().filter(g => this.getPlayerHero(g) && this.getOpponentHero(g)).length;
  });

  // ✅ Computed: Compte total de games avec faction non null
  readonly totalFactionGames = computed(() => {
    return this.games().filter(g => this.getPlayerFaction(g) && this.getOpponentFaction(g)).length;
  });

  // ✅ Computed: Matchups des héros utilisés par le joueur
  readonly heroMatchups = computed(() => {
    return this.calculateHeroMatchups();
  });

  // ✅ Computed: Matchups par faction adverse
  readonly factionMatchups = computed(() => {
    return this.calculateFactionMatchups();
  });

  // ✅ Computed: Tous les héros joués par le joueur
  readonly playerHeroes = computed(() => {
    const heroStats = new Map<string, { games: number; hero: string; heroFull: string; faction: string }>();

    for (const game of this.games()) {
      const playerHero = this.getPlayerHero(game);
      const playerFaction = this.getPlayerFaction(game);

      if (playerHero) {
        const key = playerHero;
        const existing = heroStats.get(key) || { games: 0, hero: playerHero, heroFull: playerHero, faction: playerFaction || '' };
        existing.games++;
        heroStats.set(key, existing);
      }
    }

    return Array.from(heroStats.values())
      .sort((a, b) => b.games - a.games);
  });

  // ✅ Computed: Toutes les factions jouées par le joueur
  readonly playerFactions = computed(() => {
    const factionStats = new Map<string, { games: number; faction: string }>();

    for (const game of this.games()) {
      const playerFaction = this.getPlayerFaction(game);

      if (playerFaction) {
        const existing = factionStats.get(playerFaction) || { games: 0, faction: playerFaction };
        existing.games++;
        factionStats.set(playerFaction, existing);
      }
    }

    return Array.from(factionStats.values())
      .sort((a, b) => b.games - a.games);
  });

  constructor() {
    effect(() => {
      // ✅ L'effect surveille player_id ET selectedSeason
      const playerId = this.player_id();
      const season = this.selectedSeason();

      if (playerId && season) {
        // ✅ Réinitialiser les filtres lors du changement de saison
        this.selectedPlayerHero.set('ALL');
        this.selectedPlayerFaction.set('ALL');
        this.loadGames();
      }
    });
  }

  private loadGames(): void {
    if (!this.player_id()) return;

    this.isLoading = true;

    this.playerService.get_player_history$(this.player_id(), this.selectedSeason())
      .subscribe({
        next: (response: GameModel[]) => {
          this.games.set(response);
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading games:', error);
          this.games.set([]);
          this.isLoading = false;
        }
      });
  }

  // ✅ Calcul des matchups par héros (joueur vs tous les héros adverses)
  private calculateHeroMatchups(): HeroMatchup[] {
    const matchups = new Map<string, HeroMatchup>();

    // Filtrer par héros du joueur si sélectionné
    const selectedHero = this.selectedPlayerHero();
    const filteredGames = selectedHero !== 'ALL'
      ? this.games().filter(g => this.getPlayerHero(g) === selectedHero)
      : this.games();

    for (const game of filteredGames) {
      const opponentHero = this.getOpponentHero(game);
      const opponentFaction = this.getOpponentFaction(game);

      if (!opponentHero) continue;

      const key = opponentHero;
      const existing = matchups.get(key);

      if (!existing) {
        matchups.set(key, {
          hero: opponentHero,
          heroFull: opponentHero,
          faction: opponentFaction || '',
          games: 0,
          wins: 0,
          losses: 0,
          draws: 0,
          winRate: 0
        });
      }

      const matchup = matchups.get(key)!;
      matchup.games++;

      if (game.is_draw) {
        matchup.draws++;
      } else if (this.isWin(game)) {
        matchup.wins++;
      } else {
        matchup.losses++;
      }

      matchup.winRate = matchup.games > 0 ? (matchup.wins / matchup.games) * 100 : 0;
    }

    // Trier par winRate (décroissant), puis par nombre de games (décroissant)
    return Array.from(matchups.values())
      .sort((a, b) => {
        const byWin = b.winRate - a.winRate;
        return byWin !== 0 ? byWin : b.games - a.games;
      });
  }

  // ✅ Calcul des matchups par faction adverse
  private calculateFactionMatchups(): FactionMatchup[] {
    const matchups = new Map<string, FactionMatchup>();

    // Filtrer par faction du joueur si sélectionnée
    const selectedFaction = this.selectedPlayerFaction();
    const filteredGames = selectedFaction !== 'ALL'
      ? this.games().filter(g => this.getPlayerFaction(g) === selectedFaction)
      : this.games();

    for (const game of filteredGames) {
      const opponentFaction = this.getOpponentFaction(game);

      if (!opponentFaction) continue;

      const existing = matchups.get(opponentFaction);

      if (!existing) {
        matchups.set(opponentFaction, {
          faction: opponentFaction,
          games: 0,
          wins: 0,
          losses: 0,
          draws: 0,
          winRate: 0
        });
      }

      const matchup = matchups.get(opponentFaction)!;
      matchup.games++;

      if (game.is_draw) {
        matchup.draws++;
      } else if (this.isWin(game)) {
        matchup.wins++;
      } else {
        matchup.losses++;
      }

      matchup.winRate = matchup.games > 0 ? (matchup.wins / matchup.games) * 100 : 0;
    }

    // Trier par winRate (décroissant), puis par nombre de parties (décroissant)
    return Array.from(matchups.values())
      .sort((a, b) => {
        const byWin = b.winRate - a.winRate;
        return byWin !== 0 ? byWin : b.games - a.games;
      });
  }

  // ✅ Helpers
  private isWin(game: GameModel): boolean {
    if (!this.player_id()) return false;
    return game.winner_id === this.player_id();
  }

  private getPlayerHero(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player1_hero : game.player2_hero;
  }

  private getPlayerFaction(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player1_faction : game.player2_faction;
  }

  private getOpponentHero(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player2_hero : game.player1_hero;
  }

  private getOpponentFaction(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player2_faction : game.player1_faction;
  }

  // ✅ UI Helpers
  getFactionGradient(faction: string): string {
    switch (faction.toUpperCase()) {
      case 'AX': return 'from-amber-800 to-amber-900';
      case 'BR': return 'from-red-600 to-red-700';
      case 'OR': return 'from-blue-600 to-blue-700';
      case 'MU': return 'from-green-600 to-green-700';
      case 'YZ': return 'from-purple-600 to-purple-700';
      case 'LY': return 'from-pink-600 to-pink-700';
      default: return 'from-gray-700 to-gray-800';
    }
  }

  getFactionBorderColor(faction: string): string {
    switch (faction.toUpperCase()) {
      case 'AX': return 'border-amber-500';
      case 'BR': return 'border-red-500';
      case 'OR': return 'border-blue-500';
      case 'MU': return 'border-green-500';
      case 'YZ': return 'border-purple-500';
      case 'LY': return 'border-pink-500';
      default: return 'border-gray-600';
    }
  }

  getFactionImageUrl(faction: string): string {
    return `/assets/img/faction/${faction.toUpperCase()}.webp`;
  }

  getHeroImageUrl(hero: string): string {
    return `/assets/img/hero/${hero.toLowerCase()}.jpg`;
  }

  getWinRateColor(winRate: number): string {
    if (winRate >= 60) return 'text-green-400';
    if (winRate >= 50) return 'text-yellow-400';
    if (winRate >= 40) return 'text-orange-400';
    return 'text-red-400';
  }

  getWinRateBarColor(winRate: number): string {
    if (winRate >= 60) return 'bg-green-500';
    if (winRate >= 50) return 'bg-yellow-500';
    if (winRate >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  }

  getWinRateStrokeColor(winRate: number): string {
    if (winRate >= 60) return '#22c55e'; // green-500
    if (winRate >= 50) return '#eab308'; // yellow-500
    if (winRate >= 40) return '#f97316'; // orange-500
    return '#ef4444'; // red-500
  }
}
