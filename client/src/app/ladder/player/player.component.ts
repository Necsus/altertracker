import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { PlayerSeasonStatsModel } from '../../01_models/03_business/player-season-stats.model';
import { PlayerModel } from '../../01_models/03_business/player.model';
import { SeasonModel } from '../../01_models/03_business/season.model';
import { PlayerService } from '../../03_business/player.service';
import { DeckComponent } from './deck/deck.component';
import { HistoryComponent } from './history/history.component';
import { MatchupComponent } from './matchup/matchup.component';
import { OverviewComponent } from './overview/overview.component';
import { PlayerHeaderComponent } from './player-header/player-header.component';

@Component({
  selector: 'app-player',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    PlayerHeaderComponent,
    HistoryComponent,
    OverviewComponent,
    MatchupComponent,
    DeckComponent
  ],
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
  isReloading = signal(false);
  lastReloadDate = signal<Date | null>(null);

  selectedSeason = signal<number | null>(null);
  seasons = signal<SeasonModel[]>([]);

  seasonStats = signal<PlayerSeasonStatsModel | null>(null);
  isLoadingSeasonStats = signal(false);

  readonly currentSeasonName = computed(() => {
    const season = this.selectedSeason();
    return season ? `Saison ${season}` : 'Toutes les saisons';
  });

  tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'history', label: 'Historique', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
    { id: 'matchups', label: 'Matchups', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
    { id: 'decks', label: 'Decks', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
    { id: 'palmares', label: 'Palmarès 🚫', icon: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z' },
    { id: 'vitrine', label: 'Vitrine 🚫', icon: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' }
  ];

  ngOnInit(): void {
    const playerId = this.route.snapshot.paramMap.get('player_id');
    if (playerId) {
      this.player_id.set(playerId);
      this.loadPlayer(playerId);
    } else {
      this.error.set('ID du joueur manquant');
      this.isLoading.set(false);
    }
  }

  private loadPlayer(playerId: string): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.playerService.get_player_by_id$(playerId).subscribe({
      next: (player: PlayerModel) => {
        this.player.set(player);
        this.lastReloadDate.set(player.updated_at ? new Date(player.updated_at) : null);
        this.loadSeasons();
        this.isLoading.set(false);
      },
      error: (error) => {
        this.error.set(error.error?.message || 'Erreur de chargement');
        this.isLoading.set(false);
      }
    });
  }

  private loadSeasons(): void {
    this.playerService.get_season_info$().subscribe({
      next: (response: any) => {
        const seasons: SeasonModel[] = response.seasons || [];
        this.seasons.set(seasons);

        // Sélectionner la saison courante
        const currentSeason = seasons.find(s => s.current);
        if (currentSeason) {
          this.selectedSeason.set(currentSeason.season);
          this.loadSeasonStats(currentSeason.season);
        } else if (seasons.length > 0) {
          this.selectedSeason.set(seasons[0].season);
          this.loadSeasonStats(seasons[0].season);
        }
      },
      error: (error) => {
        console.error('Erreur lors du chargement des saisons:', error);
      }
    });
  }

  // ✅ UNIQUE point de chargement des stats de saison
  private loadSeasonStats(season: number): void {
    if (!this.player_id() || this.isLoadingSeasonStats()) return;

    this.isLoadingSeasonStats.set(true);

    this.playerService.get_player_overview$(this.player_id(), season).subscribe({
      next: (stats: PlayerSeasonStatsModel) => {
        this.seasonStats.set(stats);
        this.isLoadingSeasonStats.set(false);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des stats:', err);
        this.seasonStats.set(null);
        this.isLoadingSeasonStats.set(false);
      }
    });
  }

  onSeasonChange(newSeason: number): void {
    this.selectedSeason.set(newSeason);
    this.loadSeasonStats(newSeason);
  }

  reloadPlayerData(): void {
    if (this.isReloading()) return;

    const playerId = this.player_id();
    if (!playerId) return;

    this.isReloading.set(true);

    this.playerService.get_player_reload$(playerId).subscribe({
      next: () => {
        window.location.reload();
      },
      error: (error) => {
        console.error('❌ Erreur lors du rechargement:', error);
        this.isReloading.set(false);
      }
    });
  }

  retry(): void {
    const playerId = this.route.snapshot.paramMap.get('player_id');
    if (playerId) {
      this.loadPlayer(playerId);
    }
  }
}
