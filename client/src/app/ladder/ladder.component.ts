import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

interface Player {
  id: number;
  name: string;
  country: string;
  team?: string;
  points: number;
  wins: number;
  totalGames: number;
  season: string;
}

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

  players: Player[] = [];
  teams: Team[] = [];

  filteredPlayers: Player[] = [];
  filteredTeams: Team[] = [];

  countries: string[] = [];
  seasons: string[] = [];

  currentPage: number = 1;
  pageSize: number = 50;
  totalPages: number = 1;

  totalPlayers: number = 0;
  activePlayers: number = 0;
  totalTeams: number = 0;

  Math = Math;

  constructor(private router: Router) { }

  ngOnInit(): void {
    this.loadPlayers();
    this.loadTeams();
    this.loadFilters();
  }

  loadPlayers(): void {
    // TODO: Remplacer par votre service
    const availableCountries = ['FR', 'US', 'UK', 'DE', 'ES', 'IT', 'JP', 'BR'];
    const availableSeasons = ['2024-1', '2024-2', '2025-1'];

    this.players = Array.from({ length: 100 }, (_, i) => ({
      id: i + 1,
      name: `Player ${i + 1}`,
      country: availableCountries[Math.floor(Math.random() * availableCountries.length)],
      team: i % 3 === 0 ? `Team ${Math.floor(i / 3) + 1}` : undefined,
      points: 10000 - i * 50,
      wins: Math.floor(Math.random() * 100),
      totalGames: Math.floor(Math.random() * 200) + 50,
      season: availableSeasons[Math.floor(Math.random() * availableSeasons.length)]
    }));

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
    // Extraire les pays uniques
    this.countries = [...new Set(this.players.map(p => p.country))].sort();

    // Extraire les saisons uniques
    const playerSeasons = this.players.map(p => p.season);
    const teamSeasons = this.teams.map(t => t.season);
    this.seasons = [...new Set([...playerSeasons, ...teamSeasons])].sort().reverse();
  }

  onSearchChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  applyFilters(): void {
    const query = this.searchQuery.toLowerCase().trim();

    if (this.activeTab === 'players') {
      this.filteredPlayers = this.players.filter(p => {
        // Filtre de recherche
        const matchesSearch = !query ||
          p.name.toLowerCase().includes(query) ||
          p.country.toLowerCase().includes(query) ||
          (p.team && p.team.toLowerCase().includes(query));

        // Filtre de pays
        const matchesCountry = !this.selectedCountry || p.country === this.selectedCountry;

        // Filtre de saison
        const matchesSeason = !this.selectedSeason || p.season === this.selectedSeason;

        return matchesSearch && matchesCountry && matchesSeason;
      });

      this.totalPlayers = this.filteredPlayers.length;
    } else {
      this.filteredTeams = this.teams.filter(t => {
        // Filtre de recherche
        const matchesSearch = !query ||
          t.name.toLowerCase().includes(query) ||
          t.tag.toLowerCase().includes(query);

        // Filtre de saison
        const matchesSeason = !this.selectedSeason || t.season === this.selectedSeason;

        return matchesSearch && matchesSeason;
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

  viewPlayerProfile(playerId: number): void {
    this.router.navigate(['/player', playerId]);
  }

  viewTeamProfile(teamId: number): void {
    this.router.navigate(['/team', teamId]);
  }
}