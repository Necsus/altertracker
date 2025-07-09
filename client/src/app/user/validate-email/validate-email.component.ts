import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../../03_business/auth.service';

@Component({
  selector: 'app-validate-email',
  templateUrl: './validate-email.component.html',
  imports: [CommonModule, RouterModule, TranslateModule],
})
export class ValidateEmailComponent implements OnInit {
  status: 'loading' | 'success' | 'error' | 'noresend' = 'loading';
  token: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private authService: AuthService) { }

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token');
    if (this.token) {
      this.authService.validateEmail$(this.token).subscribe({
        next: () => {
          this.status = 'success';
        },
        error: () => {
          this.status = 'error';
        }
      });
    } else {
      this.status = 'noresend';
    }
  }

  resendEmail(): void {
    if (this.token) {
      this.authService.resendValidationEmail$(this.token).subscribe({
        next: () => {
          this.status = 'success';
        },
        error: () => {
          this.status = 'error';
        }
      });
    } else {
      this.status = 'noresend';
    }
  }
}