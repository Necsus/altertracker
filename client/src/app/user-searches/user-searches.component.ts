import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserSearchModel } from '../01_models/03_business/user-search.model';
import { UserService } from '../03_business/user.service';
import { ToastService } from '../shared/services/toast/toast.service';

@Component({
  selector: 'app-user-searches',
  templateUrl: './user-searches.component.html',
  styleUrls: ['./user-searches.component.css'],
  imports: [CommonModule]
})
export class UserSearchesComponent implements OnInit {
  isLoading: boolean = false; // État de chargement
  searches: UserSearchModel[] = []; // Liste des recherches

  constructor(
    private userService: UserService,
    private toastService: ToastService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadUserSearches();
  }

  loadUserSearches(): void {
    this.isLoading = true; // Démarre le chargement
    this.userService.get_user_searches$().subscribe({
      next: (response: UserSearchModel[]) => {
        this.searches = response; // Met à jour la liste des recherches
      },
      error: (err: any) => {
        this.isLoading = false; // Arrête le chargement
        this.toastService.show(err.message, 'error', 5000);
      },
      complete: () => {
        this.isLoading = false; // Arrête le chargement
      }
    });
  }

  goSearch(url: string): void {
    this.router.navigateByUrl(url); // Redirige vers l'URL de recherche
  }

  deleteSearch(id: number): void {
    this.isLoading = true; // Démarre le chargement
    this.userService.delete_user_searche$(id).subscribe({
      next: () => {
        this.searches = this.searches.filter(search => search.id !== id);
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
}