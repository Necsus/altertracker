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
      }
    });
  }

  calculateRank(): string {
    // TODO: Implémenter le calcul du rang basé sur la saison
    return 'N/A';
  }

  calculateWinLossRatio(): string {
    if (!this.playerStats || this.playerStats.losses === 0) {
      return this.playerStats?.wins?.toString() || '0';
    }
    const ratio = (this.playerStats.wins ?? 0) / (this.playerStats.losses ?? 0);
    return ratio.toFixed(2);
  }
}
