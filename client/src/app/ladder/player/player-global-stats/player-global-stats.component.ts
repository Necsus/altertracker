import { CommonModule } from '@angular/common';
import { Component, computed, input } from '@angular/core';
import { PlayerModel } from '../../../01_models/03_business/player.model';

@Component({
  selector: 'app-player-global-stats',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './player-global-stats.component.html'
})
export class PlayerGlobalStatsComponent {
  player = input.required<PlayerModel>();

  readonly totalGames = computed(() => {
    const p = this.player();
    return (p.total_wins || 0) + (p.total_losses || 0) + (p.total_draws || 0);
  });
}