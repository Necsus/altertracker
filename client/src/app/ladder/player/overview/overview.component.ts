import { CommonModule } from '@angular/common';
import { Component, effect, inject, input } from '@angular/core';
import { PlayerSeasonStatsModel } from '../../../01_models/03_business/player-season-stats.model';
import { PlayerService } from '../../../03_business/player.service';

@Component({
  selector: 'app-player-overview',
  templateUrl: './overview.component.html',
  imports: [CommonModule]
})
export class OverviewComponent {
  player_id = input.required<string>();
  selectedSeason = input<number | null>(null);

  playerStats: PlayerSeasonStatsModel | null = null;

  private readonly playerService = inject(PlayerService);

  constructor() {
    effect(() => {
      this.loadPlayerBySeason();
    });
  }

  loadPlayerBySeason(): void {
    if (!this.player_id()) return;

    this.playerService.get_player_overview$(this.player_id(), this.selectedSeason() ?? 0).subscribe({
      next: (response: any) => {
        this.playerStats = response || null;
      },
      error: (err: any) => {
        console.error('Erreur lors du chargement des statistiques du joueur :', err);
        this.playerStats = null;
      }
    });
  }

  calculateWinLossRatio(): string {
    if (!this.playerStats || this.playerStats.losses === 0) {
      return this.playerStats?.wins?.toString() || '0';
    }
    const ratio = (this.playerStats.wins ?? 0) / (this.playerStats.losses ?? 0);
    return ratio.toFixed(2);
  }

  // ✅ Helper pour formater le temps de réflexion
  formatReflectionTime(seconds: number | null | undefined): string {
    if (!seconds || seconds === 0) return 'N/A';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}min`;
    }
    if (minutes > 0) {
      return `${minutes}min ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  }

  // ✅ Helper pour obtenir les factions triées
  getSortedFactions(): Array<{ faction: string, stats: any }> {
    if (!this.playerStats?.faction_stats) return [];

    return Object.entries(this.playerStats.faction_stats)
      .map(([faction, stats]) => ({ faction, stats }))
      .sort((a, b) => b.stats.games - a.stats.games);
  }

  // ✅ Helper pour obtenir TOUS les héros triés (pas que le top 3)
  getAllHeroes(): Array<{ hero: string, stats: any }> {
    if (!this.playerStats?.hero_stats) return [];

    return Object.entries(this.playerStats.hero_stats)
      .map(([hero, stats]) => ({ hero, stats }))
      .sort((a, b) => b.stats.games - a.stats.games);  // Tri par nombre de parties
  }

  // ✅ Garder getTopHeroes si besoin ailleurs (optionnel)
  getTopHeroes(): Array<{ hero: string, stats: any }> {
    return this.getAllHeroes().slice(0, 3);
  }

  // ✅ Helper pour la couleur du dégradé par faction
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

  // ✅ Helper pour la couleur de bordure par faction
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

  // ✅ Helper pour la couleur du texte par faction
  getFactionTextColor(faction: string): string {
    switch (faction.toUpperCase()) {
      case 'AX': return 'text-amber-400';
      case 'BR': return 'text-red-400';
      case 'OR': return 'text-blue-400';
      case 'MU': return 'text-green-400';
      case 'YZ': return 'text-purple-400';
      case 'LY': return 'text-pink-400';
      default: return 'text-gray-400';
    }
  }
}
