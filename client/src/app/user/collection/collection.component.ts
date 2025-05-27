import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { jwtDecode } from 'jwt-decode';
import { UserCollectionModel } from '../../01_models/03_business/user-collection.model';
import { AlteredService } from '../../03_business/altered.service';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { CardComponent } from '../../cards/card/card.component';
import { withLoader } from '../../shared/services/loader/loader.operator';
import { LoaderService } from '../../shared/services/loader/loader.service';

@Component({
  selector: 'app-collection',
  templateUrl: './collection.component.html',
  imports: [CommonModule, RouterModule, CardComponent]
})
export class CollectionComponent implements OnInit {
  cards!: UserCollectionModel[]; // Remplacez any par le type approprié pour vos cartes
  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private alteredService: AlteredService,
    private userService: UserService,
    private loaderService: LoaderService
  ) {
  }
  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
    this.getUserCollection();
  }
  getUserCollection(): void {
    this.userService.get_user_collection$().subscribe({
      next: (response: UserCollectionModel[]) => {
        this.cards = response;
      }
    });
  }
  importCollection(): void {
    const alteredToken = sessionStorage.getItem('altered_token');
    if (!alteredToken) {
      this.router.navigate(['/token'], { queryParams: { callback: 'collection' } });
      return;
    }
    // Décoder le token
    const decodedToken = jwtDecode(alteredToken);
    this.alteredService.getCollection$(alteredToken)
      .pipe(withLoader(this.loaderService)).subscribe({
        next: (response) => {
          const request = {
            sub: decodedToken['sub'],
            collection: response.map((card: any) => card['reference'])
          }
          this.userService.post_user_collection$(request).subscribe({
            next: (response: any) => {
              this.cards = response;
            }
          });
        },
        error: ((error) => {
          if (error.message === 'Token invalide ou expiré. Veuillez le réinsérer.') {
            console.error('Erreur 401 détectée : Redirection vers la page /token.');
            sessionStorage.removeItem('altered_token');
            sessionStorage.removeItem('cgu_altered_token');
            this.router.navigate(['/token'], { queryParams: { callback: 'collection' } }); // Redirige l'utilisateur vers la page /token
          }
        })
      });
  }
}
