import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-bga',
  templateUrl: './login-bga.component.html',
  imports: [CommonModule, ReactiveFormsModule]
})
export class LoginBgaComponent implements OnInit {
  loginForm: FormGroup;
  showPassword = signal(false);
  isLoading = signal(false);
  error = signal<string | null>(null);

  constructor(
    private fb: FormBuilder,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      login: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    // ...existing code...
  }

  // ✅ Méthode pour retirer l'attribut readonly au focus
  removeReadonly(event: FocusEvent): void {
    const input = event.target as HTMLInputElement;
    setTimeout(() => {
      input.removeAttribute('readonly');
    }, 100);
  }

  togglePasswordVisibility(): void {
    this.showPassword.set(!this.showPassword());
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading.set(true);
      this.error.set(null);

      const { login, password } = this.loginForm.value;

      // this.authService.loginBGA(login, password).subscribe({
      //   next: (response) => {
      //     this.isLoading.set(false);
      //     if (response.status === 1) {
      //       this.router.navigate(['/ladder']);
      //     } else {
      //       this.error.set(response.error || 'Erreur de connexion');
      //     }
      //   },
      //   error: (err) => {
      //     this.isLoading.set(false);
      //     this.error.set('Erreur de connexion au serveur');
      //   }
      // });
    }
  }
}