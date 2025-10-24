import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { debounceTime, distinctUntilChanged, Subject } from 'rxjs';
import { PlayerModel } from '../01_models/03_business/player.model';
import { PlayerService } from '../03_business/player.service';

interface Team {
  id: number;
  name: string;
  tag: string;
  memberCount: number;
  totalPoints: number;
  avgPoints: number;
  season: string;
}

@Component({
  selector: 'app-ladder',
  templateUrl: './ladder.component.html',
  imports: [CommonModule, FormsModule, TranslateModule]
})
export class LadderComponent implements OnInit {
  activeTab: 'players' | 'teams' = 'players';
  searchQuery: string = '';
  selectedCountry: string = '';
  selectedSeason: string = '';

  players: PlayerModel[] = [];
  teams: Team[] = [];

  filteredPlayers: PlayerModel[] = [];
  filteredTeams: Team[] = [];

  // Pour la recherche avec dropdown
  searchResults: PlayerModel[] = [];
  showSearchDropdown: boolean = false;
  isSearching: boolean = false;
  private searchSubject = new Subject<string>();


  countries: string[] = [];
  seasons: string[] = [];

  currentPage: number = 1;
  pageSize: number = 50;
  totalPages: number = 1;

  totalPlayers: number = 0;
  activePlayers: number = 0;
  totalTeams: number = 0;

  Math = Math;

  private readonly router = inject(Router);
  private readonly playerService = inject(PlayerService);

  ngOnInit(): void {
    this.loadPlayers();
    this.loadTeams();
    this.loadFilters();
    this.setupSearchAutocomplete();
  }

  setupSearchAutocomplete(): void {
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(query => {
      if (query.length >= 2) {
        this.performSearch(query);
      } else {
        this.searchResults = [];
      }
    });
  }

  onSearchInput(): void {
    this.searchSubject.next(this.searchQuery);
    this.showSearchDropdown = true;
  }


  performSearch(query: string): void {
    this.isSearching = true;
    this.playerService.search_players$(query).subscribe({
      next: (results: PlayerModel[]) => {
        this.searchResults = results.slice(0, 5); // Limiter à 5 résultats
        this.isSearching = false;
      },
      error: (error) => {
        console.error('Error searching players:', error);
        this.searchResults = [];
        this.isSearching = false;
      }
    });
  }

  selectPlayer(player: PlayerModel): void {
    this.searchQuery = '';
    this.showSearchDropdown = false;
    this.searchResults = [];
    if (!player.id && player.bga_id) {
      this.router.navigate(['/player/bga', player.bga_id]);
    } else {
      this.router.navigate(['/player', player.id]);
    }
  }

  searchOnBGA(): void {
    if (!this.searchQuery.trim()) return;

    this.isSearching = true;
    this.playerService.search_players_bga$(this.searchQuery).subscribe({
      next: (results: PlayerModel[]) => {
        this.searchResults = results.slice(0, 5); // Limiter à 5 résultats
        this.isSearching = false;
      },
      error: (error) => {
        console.error('Error searching players:', error);
        this.searchResults = [];
        this.isSearching = false;
      }
    });
  }

  closeSearchDropdown(): void {
    // Délai pour permettre au clic sur un élément de se déclencher
    setTimeout(() => {
      this.showSearchDropdown = false;
    }, 200);
  }

  loadPlayers(): void {
    // TODO: Remplacer par votre service
    const availableCountries = ['FR', 'US', 'UK', 'DE', 'ES', 'IT', 'JP', 'BR'];
    const availableSeasons = ['2024-1', '2024-2', '2025-1'];

    this.players = Array.from({ length: 100 }, (_, i) => ({
      id: `${i + 1}`,
      bga_id: 1000 + i,
      name: `Player ${i + 1}`,
      country: availableCountries[Math.floor(Math.random() * availableCountries.length)],
      team_id: i % 3 === 0 ? `team-${Math.floor(i / 3) + 1}` : null,
      team_name: i % 3 === 0 ? `Team ${Math.floor(i / 3) + 1}` : null,
      avatar_url: null,
      bio: `Bio of player ${i + 1}`,
      total_points: 10000 - i * 50,
      total_wins: Math.floor(Math.random() * 100),
      total_losses: Math.floor(Math.random() * 50),
      total_draws: Math.floor(Math.random() * 10),
      win_rate: 0,
      total_games: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
      last_game_at: new Date().toISOString(),
      // Ajouter une propriété temporaire pour la saison (ou l'obtenir via un service)
      season: availableSeasons[Math.floor(Math.random() * availableSeasons.length)]
    } as PlayerModel & { season: string }));

    // Calculer les stats dérivées
    this.players.forEach(player => {
      const wins = player.total_wins || 0;
      const losses = player.total_losses || 0;
      const draws = player.total_draws || 0;

      player.total_games = wins + losses + draws;
      player.win_rate = player.total_games > 0 ? (wins / player.total_games) * 100 : 0;
    });

    this.totalPlayers = this.players.length;
    this.activePlayers = Math.floor(this.totalPlayers * 0.7);
    this.applyFilters();
  }

  loadTeams(): void {
    // TODO: Remplacer par votre service
    const availableSeasons = ['2024-1', '2024-2', '2025-1'];

    this.teams = Array.from({ length: 30 }, (_, i) => ({
      id: i + 1,
      name: `Team ${i + 1}`,
      tag: `T${i + 1}`,
      memberCount: Math.floor(Math.random() * 20) + 5,
      totalPoints: 50000 - i * 1000,
      avgPoints: (50000 - i * 1000) / (Math.floor(Math.random() * 20) + 5),
      season: availableSeasons[Math.floor(Math.random() * availableSeasons.length)]
    }));

    this.totalTeams = this.teams.length;
    this.applyFilters();
  }

  loadFilters(): void {
    // Extraire les pays uniques (filtrer les null)
    const playerCountries = this.players
      .map(p => p.country)
      .filter((c): c is string => c !== null);
    this.countries = [...new Set(playerCountries)].sort();

    // Extraire les saisons uniques
    const playerSeasons = this.players.map((p: any) => p.season).filter(Boolean);
    const teamSeasons = this.teams.map((t: any) => t.season).filter(Boolean);
    this.seasons = [...new Set([...playerSeasons, ...teamSeasons])].sort().reverse();
  }

  onSearchChange(): void {
    // Recherche complète en appuyant sur Entrée
    if (this.searchQuery.length >= 2) {
      this.isSearching = true;
      this.playerService.search_players$(this.searchQuery).subscribe({
        next: (results: PlayerModel[]) => {
          this.filteredPlayers = results;
          this.totalPlayers = results.length;
          this.updatePagination();
          this.isSearching = false;
          this.showSearchDropdown = false;
        },
        error: (error) => {
          console.error('Error loading players:', error);
          this.isSearching = false;
        }
      });
    }
  }

  // Helper pour obtenir les initiales du joueur
  getPlayerInitials(name: string): string {
    return name
      .split(' ')
      .map(n => n.charAt(0))
      .join('')
      .toUpperCase()
      .substring(0, 2);
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  applyFilters(): void {
    if (this.activeTab === 'players') {
      this.filteredPlayers = this.players.filter(p => {
        // Filtre de pays
        const matchesCountry = !this.selectedCountry || p.country === this.selectedCountry;

        // Filtre de saison
        const matchesSeason = !this.selectedSeason || (p as any).season === this.selectedSeason;

        return matchesCountry && matchesSeason;
      });

      this.totalPlayers = this.filteredPlayers.length;
    } else {
      this.filteredTeams = this.teams.filter(t => {
        // Filtre de saison
        const matchesSeason = !this.selectedSeason || (t as any).season === this.selectedSeason;

        return matchesSeason;
      });

      this.totalTeams = this.filteredTeams.length;
    }

    this.updatePagination();
  }

  resetFilters(): void {
    this.searchQuery = '';
    this.selectedCountry = '';
    this.selectedSeason = '';
    this.currentPage = 1;
    this.searchResults = [];
    this.showSearchDropdown = false;
    this.applyFilters();
  }

  clearCountryFilter(): void {
    this.selectedCountry = '';
    this.onFilterChange();
  }

  clearSeasonFilter(): void {
    this.selectedSeason = '';
    this.onFilterChange();
  }

  updatePagination(): void {
    const total = this.activeTab === 'players' ? this.filteredPlayers.length : this.filteredTeams.length;
    this.totalPages = Math.ceil(total / this.pageSize);
  }

  getPageNumbers(): number[] {
    const maxPages = 5;
    const pages: number[] = [];
    let start = Math.max(1, this.currentPage - Math.floor(maxPages / 2));
    let end = Math.min(this.totalPages, start + maxPages - 1);

    if (end - start + 1 < maxPages) {
      start = Math.max(1, end - maxPages + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    return pages;
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  goToPage(page: number): void {
    this.currentPage = page;
  }

  viewPlayerProfile(playerId: string): void {
    this.router.navigate(['/player', playerId]);
  }

  viewTeamProfile(teamId: number): void {
    this.router.navigate(['/team', teamId]);
  }
}