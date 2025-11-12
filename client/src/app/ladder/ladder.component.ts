import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { debounceTime, Subject, take } from 'rxjs';
import { PlayerSeasonStatsModel } from '../01_models/03_business/player-season-stats.model';
import { SeasonModel } from '../01_models/03_business/season.model';
import { TeamModel } from '../01_models/03_business/team.model';
import { PlayerService } from '../03_business/player.service';
import { AuthViewService } from '../authentication/auth-view.service';

@Component({
  selector: 'app-ladder',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule, RouterLink],
  templateUrl: './ladder.component.html'
})
export class LadderComponent implements OnInit {
  private readonly playerService = inject(PlayerService);
  private readonly authService = inject(AuthViewService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  activeTab: 'players' | 'teams' = 'players';

  players: PlayerSeasonStatsModel[] = [];
  teams: TeamModel[] = [];
  seasons: SeasonModel[] = [];

  selectedSeason: number | null = null;
  selectedHero: string = ''; // Filtre héros (pour l'affichage uniquement)

  // ✅ Liste fixe des héros (basée sur les images disponibles)
  availableHeroes: string[] = [
    'Afanas',
    'Akesha',
    'Arjun',
    'Atsadi',
    'Auraq',
    'Basira',
    'Fen',
    'Gulrang',
    'Isaree',
    'Kauri',
    'Kojo',
    'Lindiwe',
    'Moyo',
    'Nadir',
    'Nevenka',
    'Rin',
    'Sierra',
    'Sigismar',
    'Sol',
    'Subhash',
    'Teija',
    'Treyst',
    'Waru',
    'Zhen'
  ];

  totalPlayers = 0;
  activePlayers = 0;
  totalTeams = 0;

  // Pagination
  currentPage = 1;
  itemsPerPage = 100;
  totalPages = 1;

  // Search
  searchQuery = '';
  searchResults: any[] = [];
  searchResultsBGA: any[] = [];  // ✅ Nouveaux résultats BGA
  showSearchDropdown = false;
  isSearching = false;
  isSearchingBGA = false;  // ✅ État de recherche BGA
  private searchSubject = new Subject<string>();

  isImporting = false;

  get isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  ngOnInit(): void {
    this.setupSearchDebounce();

    this.route.queryParams.pipe(take(1)).subscribe(params => {
      if (params['page']) {
        this.currentPage = +params['page'];
      }
      if (params['season']) {
        this.selectedSeason = +params['season'];
      }
      if (params['hero']) {
        this.selectedHero = params['hero'];
      }

      this.loadSeasons();
    });
  }

  loadSeasons(): void {
    this.playerService.get_season_info$().subscribe({
      next: (response) => {
        this.seasons = response.seasons;
        this.totalPlayers = response.total_players;

        if (!this.selectedSeason && this.seasons.length > 0) {
          this.selectedSeason = this.seasons[0].season;
          this.updateUrlParams(); // ✅ Mettre à jour l'URL
        }

        if (this.selectedSeason) {
          this.loadPlayers();
        }
      },
      error: (err) => console.error('Erreur lors du chargement des saisons :', err)
    });
  }

  loadPlayers(): void {
    if (!this.selectedSeason) return;

    this.playerService.get_season_stats$(this.selectedSeason, this.selectedHero ?? null, this.currentPage, this.itemsPerPage).subscribe({
      next: (response) => {
        this.players = response.ladder || [];
        this.totalPages = response.pagination.total_pages || 1;
        this.activePlayers = response.total_players || 0;

        // ✅ Plus besoin d'extraire les héros dynamiquement
      },
      error: (err) => console.error('Erreur lors du chargement des joueurs :', err)
    });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.updateUrlParams();
    this.loadPlayers();
  }

  onHeroFilterChange(): void {
    this.currentPage = 1;
    this.updateUrlParams();
    this.loadPlayers();
  }

  get filteredPlayers(): PlayerSeasonStatsModel[] {
    if (!this.selectedHero || this.selectedHero === '') {
      return this.players;
    }

    return this.players.filter(player => player.most_played_hero === this.selectedHero);
  }

  get filteredTeams(): TeamModel[] {
    return this.teams;
  }

  private updateUrlParams(): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        page: this.currentPage > 1 ? this.currentPage : null,
        season: this.selectedSeason,
        hero: this.selectedHero || null
      },
      queryParamsHandling: 'merge'
    });
  }

  // Navigation avec mise à jour URL
  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.updateUrlParams();
    this.loadPlayers();
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.goToPage(this.currentPage + 1);
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.goToPage(this.currentPage - 1);
    }
  }

  getVisiblePages(): Array<{ value: number | string, index: number }> {
    const pages: Array<{ value: number | string, index: number }> = [];
    const maxVisible = 7;
    let index = 0;

    if (this.totalPages <= maxVisible) {
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push({ value: i, index: index++ });
      }
    } else {
      if (this.currentPage <= 4) {
        for (let i = 1; i <= 5; i++) pages.push({ value: i, index: index++ });
        pages.push({ value: '...', index: index++ });
        pages.push({ value: this.totalPages, index: index++ });
      } else if (this.currentPage >= this.totalPages - 3) {
        pages.push({ value: 1, index: index++ });
        pages.push({ value: '...', index: index++ });
        for (let i = this.totalPages - 4; i <= this.totalPages; i++) pages.push({ value: i, index: index++ });
      } else {
        pages.push({ value: 1, index: index++ });
        pages.push({ value: '...', index: index++ });
        for (let i = this.currentPage - 1; i <= this.currentPage + 1; i++) pages.push({ value: i, index: index++ });
        pages.push({ value: '...', index: index++ });
        pages.push({ value: this.totalPages, index: index++ });
      }
    }

    return pages;
  }

  getHeroImage(heroName: string | null): string {
    if (!heroName) return '';
    return `/assets/img/hero/${heroName.toLowerCase()}.jpg`;
  }

  // Search
  setupSearchDebounce(): void {
    this.searchSubject.pipe(debounceTime(300)).subscribe(() => {
      this.performSearch();
    });
  }

  onSearchInput(): void {
    this.searchSubject.next(this.searchQuery);
  }

  performSearch(): void {
    if (this.searchQuery.length < 2) {
      this.searchResults = [];
      return;
    }

    this.isSearching = true;
    this.playerService.search_players$(this.searchQuery).subscribe({
      next: (results) => {
        this.searchResults = results;
        this.isSearching = false;
      },
      error: (err) => {
        console.error('Erreur de recherche :', err);
        this.isSearching = false;
      }
    });
  }

  onSearchChange(): void {
    if (this.searchQuery.length >= 2) {
      this.performSearch();
    }
  }

  selectPlayer(player: any): void {
    this.showSearchDropdown = false;
    this.searchQuery = '';
    this.router.navigate(['/player', player.id]);
  }

  searchOnBGA(): void {
    if (this.searchQuery.length < 2) return;

    this.isSearchingBGA = true;
    this.playerService.search_players_bga$(this.searchQuery).subscribe({
      next: (results) => {
        this.searchResultsBGA = results;
        this.isSearchingBGA = false;
        // Garder le dropdown ouvert pour afficher les résultats BGA
        this.showSearchDropdown = true;
      },
      error: (err) => {
        console.error('Erreur de recherche BGA :', err);
        this.isSearchingBGA = false;
      }
    });
  }

  selectPlayerBGA(player: any): void {
    if (!player.bga_id) return;

    // Importer le joueur depuis BGA
    this.isSearchingBGA = true;
    this.playerService.import_player_bga$(player.bga_id).subscribe({
      next: (playerId: string) => {
        this.isSearchingBGA = false;
        this.showSearchDropdown = false;
        this.searchQuery = '';
        this.searchResultsBGA = [];
        // Naviguer vers le profil du joueur importé
        this.router.navigate(['/player', playerId]);
      },
      error: (err) => {
        console.error('Erreur d\'import BGA :', err);
        this.isSearchingBGA = false;
      }
    });
  }

  getPlayerInitials(name: string): string {
    return name.charAt(0).toUpperCase();
  }

  importSeasonData(): void {
    if (!this.selectedSeason || this.isImporting) return;

    this.isImporting = true;
    this.playerService.get_import_ladder$(this.selectedSeason).subscribe({
      next: () => {
        this.isImporting = false;
        this.loadPlayers();
      },
      error: (err) => {
        console.error('Erreur import :', err);
        this.isImporting = false;
      }
    });
  }
}
