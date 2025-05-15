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

  constructor(private router: Router, private authViewService: AuthViewService) { }

  ngOnInit() {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
  }

  onLogout() {
    this.authViewService.logout();
    this.router.navigate(['/login']);
  }

  navigateToHome(): void {
    this.router.navigate(['']);
  }
}
