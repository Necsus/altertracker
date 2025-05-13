import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-token',
  templateUrl: './token.component.html',
  imports: [CommonModule, FormsModule]
})
export class TokenComponent {
  token: string = '';
  acceptedCGU: boolean = false;
  formSubmitted: boolean = false;

  constructor(private router: Router) { }

  ngOnInit() {
    const storedToken = sessionStorage.getItem('altered_token');
    const storedCGU = sessionStorage.getItem('cgu_altered_token');

    if (storedToken) {
      this.token = storedToken;
    }

    if (storedCGU === 'true') {
      this.acceptedCGU = true;
    }
  }

  onSubmit() {
    this.formSubmitted = true;

    if (this.isFormValid()) {
      sessionStorage.setItem('altered_token', this.token);
      sessionStorage.setItem('cgu_altered_token', String(this.acceptedCGU));
      this.router.navigate(['/']);
    }
  }

  isFormValid(): boolean {
    return this.isTokenValid() && this.acceptedCGU;
  }

  isTokenValid(): boolean {
    // Validation type JWT (3 parties séparées par ".")
    const jwtPattern = /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$/;
    return jwtPattern.test(this.token.trim());
  }
}