import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthViewService } from '../../authentication/auth-view.service';

@Injectable({ providedIn: 'root' })
export class PublisherGuard implements CanActivate {
  constructor(private authViewService: AuthViewService, private router: Router) { }

  canActivate(): boolean {
    if (this.authViewService.isPublisher()) {
      return true;
    } else {
      this.router.navigate(['/login']);
      return false;
    }
  }
}