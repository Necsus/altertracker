import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthViewService } from '../../authentication/auth-view.service';
import { LanguageSelectorComponent } from '../language/language-selector.component';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  imports: [CommonModule, RouterModule, TranslateModule, LanguageSelectorComponent]
})
export class HeaderComponent implements OnInit {
  isMenuOpen = false;
  isLoggedIn = false;
  isDropdownOpen = false;
  isAdmin = false;
  username: string | null = null;

  constructor(
    private router: Router,
    private authViewService: AuthViewService,
    private cdr: ChangeDetectorRef) { }

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
  }

  reloadPage(event: Event) {
    event.preventDefault();
    window.location.href = '/cards';
  }

  onLogout(): void {
    this.authViewService.logout();
  }

  navigateToHome(): void {
    this.router.navigate(['']);
  }
}
