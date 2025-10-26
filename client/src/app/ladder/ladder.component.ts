import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { debounceTime, distinctUntilChanged, Subject } from 'rxjs';
import { PlayerSeasonStatsModel } from '../01_models/03_business/player-season-stats.model';
import { PlayerModel } from '../01_models/03_business/player.model';
import { PlayerService } from '../03_business/player.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { withLoader } from '../shared/services/loader/loader.operator';
import { LoaderService } from '../shared/services/loader/loader.service';

interface Team {
  id: number;
  name: string;
  tag: string;
  memberCount: number;
  totalPoints: number;
  avgPoints: number;
  season: number;
}

@Component({
  selector: 'app-ladder',
  templateUrl: './ladder.component.html',
  imports: [CommonModule, FormsModule, TranslateModule]
})
export class LadderComponent implements OnInit {
  isLoggedIn = false;
  isAdmin = false;
  username: string | null = null;

  activeTab: 'players' | 'teams' = 'players';
  searchQuery: string = '';
  selectedCountry: string = '';
  selectedSeason: number = 23;

  seasonStats: PlayerSeasonStatsModel[] = [];
  teams: Team[] = [];

  filteredPlayers: PlayerSeasonStatsModel[] = [];
  filteredTeams: Team[] = [];

  // Pour la recherche avec dropdown
  searchResults: PlayerModel[] = [];
  showSearchDropdown: boolean = false;
  isSearching: boolean = false;
  private searchSubject = new Subject<string>();


  countries: string[] = [];
  seasons: number[] = [19, 20, 21, 22, 23];

  currentPage: number = 1;
  pageSize: number = 100; // ✅ 100 par défaut
  totalPages: number = 1;
  totalPlayers: number = 0;

  activePlayers: number = 0;
  totalTeams: number = 0;

  isLoading: boolean = false;

  Math = Math;

  isImporting: boolean = false;

  private readonly router = inject(Router);
  private readonly playerService = inject(PlayerService);
  private readonly authViewService = inject(AuthViewService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly loaderService = inject(LoaderService);

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
      if (this.isLoggedIn) {
        this.isAdmin = this.authViewService.isAdmin();
        this.username = this.authViewService.getUsername();
      } else {
        this.isAdmin = false; // Réinitialiser si l'utilisateur n'est pas connecté
        this.username = null; // Réinitialiser si l'utilisateur n'est pas connecté
      }
      this.cdr.detectChanges();
    });
    this.loadPlayers();
    this.loadTeams();
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
      this.playerService.import_player_bga$(player.bga_id).subscribe({
        next: (importedPlayer: string) => {
          this.router.navigate(['/player', importedPlayer]);
        },
        error: (error) => {
          console.error('Error importing player from BGA:', error);
        }
      });
    } else {
      this.router.navigate(['/player', player.id]);
    }
  }

  searchOnBGA(): void {
    if (!this.searchQuery.trim()) return;

    this.isSearching = true;
    this.playerService.search_players_bga$(this.searchQuery).subscribe({
      next: (results: PlayerModel[]) => {
        this.searchResults = results;
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
    this.isLoading = true;

    this.playerService.get_season_stats$(this.selectedSeason, this.currentPage, this.pageSize)
      .pipe(withLoader(this.loaderService))
      .subscribe({
        next: (response: any) => {
          // ✅ Response contient maintenant { ladder, pagination, season, total_players, ... }
          this.seasonStats = response.ladder || [];

          // ✅ Mettre à jour la pagination
          if (response.pagination) {
            this.currentPage = response.pagination.current_page;
            this.totalPages = response.pagination.total_pages;
            this.activePlayers = response.pagination.total_players;
          }

          this.loadFilters();


          this.applyFilters();
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading players:', error);
          this.isLoading = false;
        }
      });
  }

  loadTeams(): void {
    this.teams = Array.from({ length: 30 }, (_, i) => ({
      id: i + 1,
      name: `Team ${i + 1}`,
      tag: `T${i + 1}`,
      memberCount: Math.floor(Math.random() * 20) + 5,
      totalPoints: 50000 - i * 1000,
      avgPoints: (50000 - i * 1000) / (Math.floor(Math.random() * 20) + 5),
      season: 23
    }));

    // this.totalTeams = this.teams.length;
    this.applyFilters();
  }

  loadFilters(): void {
    // Extraire les pays uniques (filtrer les null)
    const playerCountries = this.seasonStats
      .map((s: PlayerSeasonStatsModel) => s.player.country)
      .filter((c): c is string => c !== null);
    this.countries = [...new Set(playerCountries)].sort();
  }

  onSearchChange(): void {
    this.searchSubject.next(this.searchQuery);
    this.showSearchDropdown = true;
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

  /**
   * ✅ Génère la liste des pages visibles pour la pagination
   * Affiche : [1] ... [4] [5] [6] ... [16]
   */
  getVisiblePages(): (number | string)[] {
    const pages: (number | string)[] = [];
    const maxVisible = 5; // Nombre max de pages visibles autour de la page actuelle
    const halfVisible = Math.floor(maxVisible / 2);

    if (this.totalPages <= maxVisible + 2) {
      // Si peu de pages, afficher toutes
      for (let i = 1; i <= this.totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Toujours afficher la première page
      pages.push(1);

      // Calculer la plage autour de la page actuelle
      let startPage = Math.max(2, this.currentPage - halfVisible);
      let endPage = Math.min(this.totalPages - 1, this.currentPage + halfVisible);

      // Ajuster si on est près du début
      if (this.currentPage <= halfVisible + 1) {
        endPage = maxVisible;
      }

      // Ajuster si on est près de la fin
      if (this.currentPage >= this.totalPages - halfVisible) {
        startPage = this.totalPages - maxVisible + 1;
      }

      // Ajouter "..." si nécessaire avant
      if (startPage > 2) {
        pages.push('...');
      }

      // Ajouter les pages du milieu
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }

      // Ajouter "..." si nécessaire après
      if (endPage < this.totalPages - 1) {
        pages.push('...');
      }

      // Toujours afficher la dernière page
      pages.push(this.totalPages);
    }

    return pages;
  }

  onFilterChange(): void {
    this.currentPage = 1; // ✅ Reset à la page 1 lors d'un changement de filtre
    this.loadPlayers(); // ✅ Recharger les données
  }

  applyFilters(): void {
    if (this.activeTab === 'players') {
      this.filteredPlayers = this.seasonStats.filter((s: PlayerSeasonStatsModel) => {
        // Filtre de pays
        const matchesCountry = !this.selectedCountry || s.player.country === this.selectedCountry;

        return matchesCountry;
      });
    } else {
      this.filteredTeams = this.teams.filter(t => {
        // Filtre de saison
        const matchesSeason = !this.selectedSeason || (t as any).season === this.selectedSeason;

        return matchesSeason;
      });

      // this.totalTeams = this.filteredTeams.length;
    }

    // this.updatePagination();
  }

  resetFilters(): void {
    this.searchQuery = '';
    this.selectedCountry = '';
    this.selectedSeason = 23;
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
    this.selectedSeason = 23;
    this.onFilterChange();
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadPlayers();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadPlayers();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  goToPage(page: number): void {
    if (page !== this.currentPage && page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadPlayers();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  // ✅ Nouvelle méthode pour changer la taille de page
  changePageSize(newSize: number): void {
    this.pageSize = newSize;
    this.currentPage = 1;
    this.loadPlayers();
  }

  viewPlayerProfile(playerId: string): void {
    this.router.navigate(['/player', playerId]);
  }

  viewTeamProfile(teamId: number): void {
    this.router.navigate(['/team', teamId]);
  }

  importSeasonData(): void {
    if (!this.isAdmin) return;
    this.isImporting = true;
    const season = this.selectedSeason;
    this.playerService.get_import_ladder$(season)
      .pipe(withLoader(this.loaderService)).subscribe({
        next: (stats: any) => {
          console.log('Season stats imported:', stats);
          this.isImporting = false;
        },
        error: (error) => {
          console.error('Error importing season stats:', error);
          this.isImporting = false;
        }
      });
  }
}
