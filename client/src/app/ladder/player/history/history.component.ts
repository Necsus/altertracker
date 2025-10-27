import { CommonModule } from '@angular/common';
import { Component, effect, inject, input } from '@angular/core';
import { GameHelper, GameModel } from '../../../01_models/03_business/game.model';
import { PlayerService } from '../../../03_business/player.service';

interface GameStats {
  wins: number;
  losses: number;
  draws: number;
}

@Component({
  selector: 'app-player-history',
  standalone: true,
  templateUrl: './history.component.html',
  imports: [CommonModule]
})
export class HistoryComponent {
  player_id = input.required<string>();
  selectedSeason = input<number | null>(null);

  games: GameModel[] = [];
  isLoading = false;
  expandedGame: string | null = null;

  // Pagination
  currentPage = 1;
  totalPages = 1;
  totalGames = 0;

  // Stats
  stats: GameStats = {
    wins: 0,
    losses: 0,
    draws: 0
  };
  currentStreak = 0;


  private readonly playerService = inject(PlayerService);

  constructor() {
    effect(() => {
      this.loadGames();
    });
  }

  private loadGames(): void {
    if (!this.player_id()) return;

    this.isLoading = true;

    // TODO: Appeler votre service pour récupérer les parties
    this.playerService.get_player_history$(this.player_id(), this.selectedSeason() || 0)
      .subscribe({
        next: (response: GameModel[]) => {
          this.games = response;
          this.totalGames = response.length;
          // this.totalPages = Math.ceil(this.totalGames / 10); // Assuming 10 games per page
          this.calculateStats();
          this.calculateStreak();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading games:', error);
          this.games = [];
          this.totalGames = 0;
          this.isLoading = false;
        }
      });
  }

  private calculateStats(): void {
    this.stats = {
      wins: this.games.filter(g => this.isWin(g)).length,
      losses: this.games.filter(g => this.isLoss(g) && !g.is_draw).length,
      draws: this.games.filter(g => g.is_draw).length
    };
  }

  private calculateStreak(): void {
    let streak = 0;
    for (const game of this.games) {
      if (this.isWin(game)) {
        streak = streak >= 0 ? streak + 1 : 1;
      } else if (this.isLoss(game) && !game.is_draw) {
        streak = streak <= 0 ? streak - 1 : -1;
      }
    }
    this.currentStreak = streak;
  }

  isWin(game: GameModel): boolean {
    if (!this.player_id()) return false;
    return GameHelper.isPlayerWinner(game, this.player_id());
  }

  isLoss(game: GameModel): boolean {
    return !this.isWin(game) && !game.is_draw;
  }

  getOpponentName(game: GameModel): string {
    if (!this.player_id()) return 'Unknown';
    return GameHelper.getOpponentName(game, this.player_id()) || 'Unknown';
  }

  getOpponentCountry(game: GameModel): string | undefined {
    // TODO: Récupérer le pays de l'adversaire depuis les données du joueur
    return undefined;
  }

  formatDuration(minutes: number): string {
    return GameHelper.formatDuration(minutes);
  }

  toggleDetails(gameId: string): void {
    this.expandedGame = this.expandedGame === gameId ? null : gameId;
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadGames();
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadGames();
    }
  }
}
