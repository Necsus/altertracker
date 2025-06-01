import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { UserSearchModel } from '../../01_models/03_business/user-search.model';
import { UserService } from '../../03_business/user.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-save-search',
  templateUrl: './save-search.component.html',
  styleUrls: ['save-search.component.css'],
  imports: [CommonModule, FormsModule, TranslateModule]
})
export class SaveSearchComponent {
  @Input() canSaveSearch: boolean = false; // Indique si l'utilisateur peut sauvegarder une recherche
  sliderOpen: boolean = false; // État du slider
  searchName: string = ''; // Nom de la recherche
  isLoading: boolean = false; // État de chargement
  lastSearchUrl: string | null = null; // Dernière URL de recherche
  searches: UserSearchModel[] = []; // Liste des recherches

  constructor(
    private userService: UserService,
    private toastService: ToastService,
    private router: Router
  ) { }

  toggleSlider(): void {
    this.sliderOpen = !this.sliderOpen; // Ouvre/ferme le slider
    this.updateBodyScroll();
    this.lastSearchUrl = sessionStorage.getItem('lastSearchUrl');
    this.isLoading = true; // Démarre le chargement
    this.userService.get_user_searches$().subscribe({
      next: (response: UserSearchModel[]) => {
        this.searches = response; // Met à jour la liste des recherches
      },
      error: (err: any) => {
        this.isLoading = false;
        this.toastService.show(err.message, 'error', 5000);
      },
      complete: () => {
        this.isLoading = false; // Arrête le chargement
      }
    });
  }

  closeSlider(): void {
    this.sliderOpen = false; // Ferme le slider
    this.updateBodyScroll();
  }

  saveSearch(): void {
    if (this.searchName.trim()) {
      this.isLoading = true; // Démarre le chargement
      let request = <UserSearchModel>{
        name_search: this.searchName.trim(),
        url_search: this.lastSearchUrl
      };
      this.userService.post_user_search$(request).subscribe({
        next: (response: UserSearchModel) => {
          this.searches.unshift(response); // Ajoute la recherche à la liste
          this.toastService.show('Recherche sauvegardée avec succès !', 'success', 5000);
        },
        error: (err: any) => {
          this.isLoading = false;
          this.toastService.show(err.message, 'error', 5000);
        },
        complete: () => {
          this.searchName = ''; // Réinitialise le champ
          this.isLoading = false; // Arrête le chargement
        }
      });
    } else {
      console.error('Le nom de la recherche est vide.');
    }
  }

  goSearch(url: string): void {
    this.closeSlider(); // Ferme le slider
    this.router.navigateByUrl(url); // Redirige vers l'URL de recherche
  }

  private updateBodyScroll(): void {
    if (this.sliderOpen) {
      document.body.classList.add('overflow-hidden');
    } else {
      document.body.classList.remove('overflow-hidden');
    }
  }
}