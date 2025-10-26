import { CommonModule } from '@angular/common';
import { Component, input, OnInit } from '@angular/core';
import { PlayerModel } from '../../../01_models/03_business/player.model';

@Component({
  selector: 'app-player-overview',
  templateUrl: './overview.component.html',
  imports: [CommonModule]
})
export class OverviewComponent implements OnInit {
  player_id = input.required<string>();
  selectedSeason = input<number | null>(null);

  player: PlayerModel | null = null;

  ngOnInit(): void {
    // Initialisation si nécessaire
  }

  calculateRank(): string {
    // TODO: Implémenter le calcul du rang basé sur la saison
    return 'N/A';
  }

  calculateWinLossRatio(): string {
    if (!this.player || this.player.total_losses === 0) {
      return this.player?.total_wins?.toString() || '0';
    }
    const ratio = (this.player.total_wins ?? 0) / (this.player.total_losses ?? 0);
    return ratio.toFixed(2);
  }
}
