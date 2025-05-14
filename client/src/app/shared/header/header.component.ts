import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  imports: [CommonModule, RouterModule]
})
export class HeaderComponent {
  isMenuOpen = false;

  constructor(private router: Router) { }

  navigateToHome(): void {
    this.router.navigate(['']);
  }
}
