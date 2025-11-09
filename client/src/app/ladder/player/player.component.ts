import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { PlayerSeasonStatsModel } from '../../01_models/03_business/player-season-stats.model';
import { PlayerModel } from '../../01_models/03_business/player.model';
import { SeasonModel } from '../../01_models/03_business/season.model';
import { PlayerService } from '../../03_business/player.service';
import { HistoryComponent } from './history/history.component';
import { OverviewComponent } from './overview/overview.component';

@Component({
  selector: 'app-player',
  standalone: true,
  imports: [CommonModule, FormsModule, HistoryComponent, OverviewComponent],
  templateUrl: './player.component.html'
})
export class PlayerComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly playerService = inject(PlayerService);

  player_id = signal<string>('');
  player = signal<PlayerModel | null>(null);
  isLoading = signal(true);
  error = signal<string | null>(null);
  activeTab = signal('overview');

  selectedSeason = signal<number | null>(null);
  seasons = signal<SeasonModel[]>([]);

  // ✅ Ajout des stats de saison pour le héros
  playerStats = signal<PlayerSeasonStatsModel | null>(null);

  lastReloadDate = signal<Date | null>(null);
  isReloading = signal(false);

  tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'history', label: 'Historique', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
    { id: 'matchups', label: 'Matchups', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
    { id: 'decks', label: 'Decks', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' }
  ];

  ngOnInit(): void {
    const playerId = this.route.snapshot.paramMap.get('player_id');
    if (playerId) {
      this.loadPlayer(playerId);
      this.loadSeasons();
    } else {
      this.error.set('ID du joueur manquant');
      this.isLoading.set(false);
    }
  }

  loadSeasons(): void {
    this.playerService.get_season_info$().subscribe({
      next: (response: any) => {
        this.seasons.set(response.seasons || []);
        const currentSeason = response.seasons.find((s: SeasonModel) => s.current);
        if (currentSeason) {
          this.selectedSeason.set(currentSeason.season);
          this.loadPlayerStats(currentSeason.season);
        } else if (this.seasons.length > 0) {
          this.selectedSeason.set(response.seasons[0].season);
          this.loadPlayerStats(response.seasons[0].season);
        }
      },
      error: (error) => {
        console.error('Erreur lors du chargement des saisons:', error);
      }
    });
  }

  loadPlayer(playerId: string): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.playerService.get_player_by_id$(playerId).subscribe({
      next: (player: PlayerModel) => {
        this.player_id.set(playerId);
        this.player.set(player);
        this.isLoading.set(false);
        this.lastReloadDate.set(new Date(player.updated_at ?? ''));
      },
      error: (error) => {
        this.error.set(error.error?.message || 'Erreur de chargement');
        this.isLoading.set(false);
      }
    });
  }

  // ✅ Charger les stats de saison pour récupérer le héros le plus joué
  loadPlayerStats(season: number): void {
    if (!this.player_id()) return;

    this.playerService.get_player_overview$(this.player_id(), season).subscribe({
      next: (stats: any) => {
        this.playerStats.set(stats);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des stats:', err);
        this.playerStats.set(null);
      }
    });
  }

  onSeasonChange(newSeason: number): void {
    this.selectedSeason.set(newSeason);
    this.loadPlayerStats(newSeason);
  }

  // ✅ Helper pour obtenir l'URL de l'image du héros
  getHeroImageUrl(): string {
    const hero = this.playerStats()?.most_played_hero;
    if (!hero) return '';
    return `/assets/img/hero/${hero.toLowerCase()}.jpg`;
  }

  // ✅ Helper pour obtenir la faction du héros principal
  getMostPlayedFaction(): string | null {
    return this.playerStats()?.most_played_faction || null;
  }

  // ✅ Helper pour le dégradé de faction
  getFactionGradient(faction: string | null): string {
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

  // ✅ Méthode pour recharger les données du joueur
  reloadPlayerData(): void {
    if (this.isReloading()) {
      console.log('⚠️  Rechargement déjà en cours');
      return;
    }

    const playerId = this.player_id();
    if (!playerId) {
      console.error('❌ Aucun player_id disponible');
      return;
    }

    console.log('🔄 Rechargement des données du joueur...');
    this.isReloading.set(true);

    this.playerService.get_player_reload$(playerId).subscribe({
      next: (result: any) => {
        window.location.reload();
      },
      error: (error) => {
        console.error('❌ Erreur lors du rechargement:', error);
        this.isReloading.set(false);
      }
    });
  }

  retry(): void {
    const playerId = this.route.snapshot.paramMap.get('id');
    if (playerId) {
      this.loadPlayer(playerId);
    }
  }
}
