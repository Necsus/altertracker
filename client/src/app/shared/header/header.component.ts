import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { AuthViewService } from '../../authentication/auth-view.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  imports: [CommonModule, RouterModule]
})
export class HeaderComponent implements OnInit {
  isMenuOpen = false;
  isLoggedIn = false;
  isDropdownOpen = false;
  isAdmin = false;
  username: string | null = null;

  constructor(private router: Router, private authViewService: AuthViewService) { }

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
    });
  }

  onLogout(): void {
    this.authViewService.logout();
  }

  navigateToHome(): void {
    this.router.navigate(['']);
  }
}
