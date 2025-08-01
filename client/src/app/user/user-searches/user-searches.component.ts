import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { UserSearchModel } from '../../01_models/03_business/user-search.model';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-user-searches',
  templateUrl: './user-searches.component.html',
  styleUrls: ['./user-searches.component.css'],
  imports: [CommonModule, TranslateModule]
})
export class UserSearchesComponent implements OnInit {
  isLoading: boolean = false; // État de chargement
  searches: UserSearchModel[] = []; // Liste des recherches
  discordLinked: boolean = false; // État de la liaison Discord

  constructor(
    private userService: UserService,
    private toastService: ToastService,
    private authViewService: AuthViewService,
    private router: Router,
    private loaderService: LoaderService
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
      this.discordLinked = this.authViewService.getDiscordIdLinked() ?? false;
    });
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

  toggleFavorite(search: UserSearchModel): void {
    if (!this.discordLinked) {
      this.toastService.show('Veuillez rejoindre le serveur Discord et lier votre compte Discord pour activer les notifications.', 'info', 5000);
      this.router.navigate(['/me']);
      return;
    }
    search.active_favorite = !search.active_favorite;
    this.userService.post_user_search_alerts$(search)
      .pipe(withLoader(this.loaderService)).subscribe({
        next: () => { },
        error: (err: any) => {// Rétablit l'état précédent en cas d'erreur
          this.toastService.show(err.message, 'error', 5000);
          if (search) {
            search.active_favorite = !search.active_favorite;
          }
        },
      });
  }

  deleteSearch(id: number): void {
    this.isLoading = true; // Démarre le chargement
    this.userService.delete_user_search$(id).subscribe({
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

  toggleSearchNotifications(search: UserSearchModel): void {
    if (!this.discordLinked) {
      this.toastService.show('Veuillez rejoindre le serveur Discord et lier votre compte Discord pour activer les notifications.', 'info', 5000);
      this.router.navigate(['/me']);
      return;
    }
    search.active_notification = !search.active_notification;
    this.userService.post_user_search_alerts$(search)
      .pipe(withLoader(this.loaderService)).subscribe({
        next: () => { },
        error: (err: any) => {// Rétablit l'état précédent en cas d'erreur
          this.toastService.show(err.message, 'error', 5000);
          if (search) {
            search.active_notification = !search.active_notification;
          }
        },
      });
  }
}