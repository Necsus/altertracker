import { CommonModule } from '@angular/common';
import { Component, effect, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { GameHelper, GameModel } from '../../../01_models/03_business/game.model';
import { PlayerService } from '../../../03_business/player.service';
import { AuthViewService } from '../../../authentication/auth-view.service';

interface GameStats {
  wins: number;
  losses: number;
  draws: number;
}

@Component({
  selector: 'app-player-history',
  standalone: true,
  templateUrl: './history.component.html',
  imports: [CommonModule, RouterLink]
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
  loadingTableId: number | null = null;

  private readonly playerService = inject(PlayerService);
  private readonly authViewService = inject(AuthViewService);

  get isActiveBga(): boolean {
    return this.authViewService.activeBga();
  }

  constructor() {
    effect(() => {
      this.loadGames();
    });
  }

  private loadGames(): void {
    if (!this.player_id()) return;

    this.isLoading = true;

    this.playerService.get_player_history$(this.player_id(), this.selectedSeason() || 0)
      .subscribe({
        next: (response: GameModel[]) => {
          this.games = response;
          this.totalGames = response.length;
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

  getOpponentId(game: GameModel): string {
    return game.player1_id === this.player_id() ? game.player2_id : game.player1_id;
  }

  getOpponentCountry(game: GameModel): string | undefined {
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

  loadTable(table_id: number): void {
    this.loadingTableId = table_id;
    this.playerService.get_import_table$(table_id)
      .subscribe({
        next: (response: any) => {
          this.loadingTableId = null;
          console.log('Table data:', response);
          // ✅ Recharger l'historique pour afficher les nouvelles infos
          this.loadGames();
        },
        error: (error: any) => {
          this.loadingTableId = null;
          console.error('Error loading table data:', error);
        }
      });
  }

  // ✅ Helper pour obtenir l'URL de l'image de faction
  getFactionImageUrl(faction: string | undefined): string {
    if (!faction) return '/assets/img/faction/NEUTRAL.webp';
    return `/assets/img/faction/${faction.toUpperCase()}.webp`;
  }

  // ✅ Helper pour obtenir l'URL de l'image de héros
  getHeroImageUrl(hero: string | undefined): string {
    if (!hero) return '/assets/img/hero/unknown.jpg';
    return `/assets/img/hero/${hero.toLowerCase()}.jpg`;
  }

  // ✅ Helper pour obtenir faction/hero du joueur actuel
  getPlayerFaction(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player1_faction : game.player2_faction;
  }

  getPlayerHero(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player1_hero : game.player2_hero;
  }

  // ✅ Helper pour obtenir faction/hero de l'adversaire
  getOpponentFaction(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player2_faction : game.player1_faction;
  }

  getOpponentHero(game: GameModel): string | undefined {
    return game.player1_id === this.player_id() ? game.player2_hero : game.player1_hero;
  }

  // ✅ Helper pour vérifier si les infos du deck sont disponibles
  hasPlayerFaction(game: GameModel): boolean {
    const faction = this.getPlayerFaction(game);
    return !!faction;
  }

  hasPlayerHero(game: GameModel): boolean {
    const hero = this.getPlayerHero(game);
    return !!hero;
  }

  hasOpponentFaction(game: GameModel): boolean {
    const faction = this.getOpponentFaction(game);
    return !!faction;
  }

  hasOpponentHero(game: GameModel): boolean {
    const hero = this.getOpponentHero(game);
    return !!hero;
  }

  // ✅ Garder hasPlayerDeckInfo pour la compatibilité (faction + hero)
  hasPlayerDeckInfo(game: GameModel): boolean {
    return this.hasPlayerFaction(game) && this.hasPlayerHero(game);
  }

  hasOpponentDeckInfo(game: GameModel): boolean {
    return this.hasOpponentFaction(game) && this.hasOpponentHero(game);
  }

  // ✅ Helper pour obtenir la couleur de dégradé par faction
  getFactionGradient(faction: string | undefined): string {
    if (!faction) return 'from-gray-700 to-transparent';

    switch (faction.toUpperCase()) {
      case 'AX':
        return 'from-amber-950 to-transparent'; // Marron
      case 'BR':
        return 'from-red-600 to-transparent'; // Rouge
      case 'OR':
        return 'from-blue-600 to-transparent'; // Bleu
      case 'MU':
        return 'from-green-600 to-transparent'; // Vert
      case 'YZ':
        return 'from-purple-600 to-transparent'; // Violet
      case 'LY':
        return 'from-pink-600 to-transparent'; // Rose
      default:
        return 'from-gray-700 to-transparent';
    }
  }

  // ✅ Helper pour obtenir la couleur de bordure par faction
  getFactionBorderColor(faction: string | undefined): string {
    if (!faction) return 'border-gray-700';

    switch (faction.toUpperCase()) {
      case 'AX':
        return 'border-amber-950';
      case 'BR':
        return 'border-red-500';
      case 'OR':
        return 'border-blue-500';
      case 'MU':
        return 'border-green-500';
      case 'YZ':
        return 'border-purple-500';
      case 'LY':
        return 'border-pink-500';
      default:
        return 'border-gray-700';
    }
  }

  /**
   * Formate le temps de réflexion en minutes:secondes
   * @param seconds Temps en secondes
   * @returns Format "Xmin Ys" ou "Xs" si moins d'une minute
   */
  formatReflectionTime(seconds: number | null | undefined): string {
    if (!seconds || seconds === 0) return 'N/A';

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes === 0) {
      return `${remainingSeconds}s`;
    }

    return `${minutes}min ${remainingSeconds}s`;
  }

  /**
   * Calcule le temps de réflexion moyen par tour
   * @param reflexionTime Temps total de réflexion en secondes
   * @param nbTurns Nombre de tours joués
   * @returns Temps moyen par tour en secondes
   */
  calculateAverageReflectionTime(reflexionTime: number | null | undefined, nbTurns: number | null | undefined): number | null {
    if (!reflexionTime || !nbTurns || nbTurns === 0) return null;
    return Math.round(reflexionTime / nbTurns);
  }

  /**
   * Formate le temps de réflexion moyen avec indication du nombre de tours
   * @param reflexionTime Temps total en secondes
   * @param nbTurns Nombre de tours
   * @returns Format "Xmin Ys/tour (Y tours)" ou "N/A"
   */
  formatAverageReflectionTime(reflexionTime: number | null | undefined, nbTurns: number | null | undefined): string {
    const avgTime = this.calculateAverageReflectionTime(reflexionTime, nbTurns);

    if (!avgTime) return 'N/A';

    const minutes = Math.floor(avgTime / 60);
    const seconds = avgTime % 60;

    if (minutes === 0) {
      return `${seconds}s/tour`;
    }

    return `${minutes}min ${seconds}s/tour`;
  }
}
