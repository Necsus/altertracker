import { CommonModule } from '@angular/common';
import { Component, computed, input } from '@angular/core';
import { PlayerSeasonStatsModel } from '../../../01_models/03_business/player-season-stats.model';
import { PlayerModel } from '../../../01_models/03_business/player.model';

@Component({
  selector: 'app-player-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './player-header.component.html'
})
export class PlayerHeaderComponent {
  // ✅ Inputs (données passées par le parent)
  player = input.required<PlayerModel>();
  seasonStats = input<PlayerSeasonStatsModel | null>(null);
  isReloading = input<boolean>(false);
  lastReloadDate = input<Date | null>(null);

  // ✅ Computed signals
  readonly heroImageUrl = computed(() => {
    const hero = this.seasonStats()?.most_played_hero;
    return hero ? `/assets/img/hero/${hero.toLowerCase()}.jpg` : '';
  });

  readonly factionGradient = computed(() => {
    const faction = this.seasonStats()?.most_played_faction;
    return this.getFactionGradient(faction);
  });

  readonly totalGames = computed(() => {
    const stats = this.seasonStats();
    if (!stats) return 0;
    return (stats.wins || 0) + (stats.losses || 0) + (stats.draws || 0);
  });

  getFactionGradient(faction: string | null | undefined): string {
    if (!faction) return 'from-gray-800 via-gray-900 to-black';

    switch (faction.toUpperCase()) {
      case 'AX': return 'from-amber-900/90 via-amber-800/80 to-orange-900/90';
      case 'BR': return 'from-red-900/90 via-red-800/80 to-red-950/90';
      case 'OR': return 'from-blue-900/90 via-blue-800/80 to-blue-950/90';
      case 'MU': return 'from-green-900/90 via-green-800/80 to-green-950/90';
      case 'YZ': return 'from-purple-900/90 via-purple-800/80 to-purple-950/90';
      case 'LY': return 'from-pink-900/90 via-pink-800/80 to-pink-950/90';
      default: return 'from-gray-800/90 via-gray-900/80 to-black/90';
    }
  }
}