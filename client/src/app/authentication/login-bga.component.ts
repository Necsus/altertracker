import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../03_business/auth.service';

@Component({
  selector: 'app-login-bga',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login-bga.component.html',
  styleUrls: ['./login-bga.component.css']
})
export class LoginBgaComponent {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  loginForm: FormGroup;
  isLoading = signal(false);
  error = signal<string | null>(null);
  showPassword = signal(false);

  constructor() {
    this.loginForm = this.fb.group({
      login: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.error.set('Veuillez remplir tous les champs correctement');
      return;
    }

    this.isLoading.set(true);
    this.error.set(null);

    // this.authService.login(this.loginForm.value).subscribe({
    //   next: (response) => {
    //     console.log('✅ Connexion réussie:', response);
    //     this.isLoading.set(false);
    //     this.router.navigate(['/ladder']);
    //   },
    //   error: (error) => {
    //     console.error('❌ Erreur de connexion:', error);
    //     this.isLoading.set(false);
    //     this.error.set(error.error?.message || 'Identifiants incorrects');
    //   }
    // });
  }

  loginWithBGA(): void {
    this.isLoading.set(true);
    this.error.set(null);

    try {
      // this.authService.loginWithBGA();
    } catch (err) {
      console.error('❌ Erreur lors de la redirection BGA:', err);
      this.isLoading.set(false);
      this.error.set('Impossible de se connecter à BoardGameArena');
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword.set(!this.showPassword());
  }
}