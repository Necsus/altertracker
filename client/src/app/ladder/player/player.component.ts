import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PlayerModel } from '../../01_models/03_business/player.model';
import { PlayerService } from '../../03_business/player.service';

@Component({
  selector: 'app-player',
  standalone: true,
  templateUrl: './player.component.html',
  imports: [CommonModule]
})
export class PlayerComponent implements OnInit {
  player: PlayerModel | null = null;
  activeTab: 'history' | 'overview' | 'matchups' | 'decks' = 'history'; // ✅ Historique par défaut
  error: string | null = null;
  isLoading = false;

  private readonly activatedRoute = inject(ActivatedRoute);
  private readonly playerService = inject(PlayerService);
  private readonly router = inject(Router);
  private playerId: string | null = null;

  // ✅ Historique en premier
  readonly tabs = [
    {
      id: 'history',
      label: 'Historique',
      icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
    },
    {
      id: 'overview',
      label: 'Vue d\'ensemble',
      icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
    },
    {
      id: 'matchups',
      label: 'Matchups',
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'
    },
    {
      id: 'decks',
      label: 'Decks',
      icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10'
    }
  ] as const;

  ngOnInit(): void {
    this.playerId = this.activatedRoute.snapshot.paramMap.get('player_id');
    if (this.playerId) {
      this.loadPlayer(this.playerId);
    } else {
      this.error = 'ID de joueur manquant';
    }
  }

  private loadPlayer(player_id: string): void {
    this.isLoading = true;
    this.error = null;

    this.playerService.get_player_by_id$(player_id).subscribe({
      next: (player) => {
        this.player = player;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading player:', error);
        this.error = error.error?.message || 'Impossible de charger le profil du joueur';
        this.isLoading = false;
      }
    });
  }

  calculateRank(): string {
    return '#1';
  }

  calculateWinLossRatio(): string {
    const wins = this.player?.total_wins || 0;
    const losses = this.player?.total_losses || 0;

    if (losses === 0) {
      return wins > 0 ? `${wins}.00` : '0.00';
    }

    const ratio = wins / losses;
    return ratio.toFixed(2);
  }

  retry(): void {
    if (this.playerId) {
      this.loadPlayer(this.playerId);
    }
  }

  goBack(): void {
    this.router.navigate(['/ladder']);
  }
}