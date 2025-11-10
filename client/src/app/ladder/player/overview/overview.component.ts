import { CommonModule } from '@angular/common';
import { Component, input } from '@angular/core';
import { PlayerSeasonStatsModel } from '../../../01_models/03_business/player-season-stats.model';
import { PlayerModel } from '../../../01_models/03_business/player.model';
import { PlayerGlobalStatsComponent } from '../player-global-stats/player-global-stats.component';

@Component({
  selector: 'app-player-overview',
  standalone: true,
  imports: [CommonModule, PlayerGlobalStatsComponent],
  templateUrl: './overview.component.html'
})
export class OverviewComponent {
  // ✅ Reçoit les stats ET le player depuis le parent
  seasonStats = input.required<PlayerSeasonStatsModel | null>();
  player = input.required<PlayerModel>();

  calculateWinLossRatio(): string {
    const stats = this.seasonStats();
    if (!stats || stats.losses === 0) {
      return stats?.wins?.toString() || '0';
    }
    const ratio = (stats.wins ?? 0) / (stats.losses ?? 0);
    return ratio.toFixed(2);
  }

  getSortedFactions(): Array<{ faction: string, stats: any }> {
    const stats = this.seasonStats();
    if (!stats?.faction_stats) return [];

    return Object.entries(stats.faction_stats)
      .map(([faction, stats]) => ({ faction, stats }))
      .sort((a, b) => b.stats.games - a.stats.games);
  }

  getAllHeroes(): Array<{ hero: string, stats: any }> {
    const stats = this.seasonStats();
    if (!stats?.hero_stats) return [];

    return Object.entries(stats.hero_stats)
      .map(([hero, stats]) => ({ hero, stats }))
      .sort((a, b) => b.stats.games - a.stats.games);
  }

  formatTotalReflectionTime(): string {
    const stats = this.seasonStats();
    if (!stats?.total_reflexion_time || !stats?.total_turns) return 'N/A';

    const totalSeconds = stats.total_reflexion_time;
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    let result = '';
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0) result += `${minutes}min `;
    if (seconds > 0 && hours === 0) result += `${seconds}s`;

    return result.trim();
  }

  calculateAverageReflectionTime(): number | null {
    const stats = this.seasonStats();
    if (!stats?.total_reflexion_time || !stats?.total_turns || stats.total_turns === 0) return null;
    return Math.round(stats.total_reflexion_time / stats.total_turns);
  }

  formatReflectionTime(): string {
    const avgTime = this.calculateAverageReflectionTime();
    if (!avgTime) return 'N/A';

    const minutes = Math.floor(avgTime / 60);
    const seconds = avgTime % 60;

    if (minutes === 0) return `${seconds}s/tour`;
    return `${minutes}min ${seconds}s/tour`;
  }

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
