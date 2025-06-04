import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../03_business/auth.service';
import { withLoader } from '../shared/services/loader/loader.operator';
import { LoaderService } from '../shared/services/loader/loader.service';
import { ToastService } from '../shared/services/toast/toast.service';
import { AuthViewService } from './auth-view.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private toastService: ToastService,
    private router: Router,
    private authViewService: AuthViewService,
    private loaderService: LoaderService) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (status) {
        this.router.navigate(['/']);
      }
    });
    this.loginForm = this.fb.group({
      email: [''],
      password: ['']
    });
  }

  onSubmit(): void {
    const formValues = this.loginForm.value;
    this.authService.login$(formValues.email, formValues.password)
      .pipe(withLoader(this.loaderService))
      .subscribe({
        next: () => {
          this.authViewService.loggedIn.next(true);
          this.toastService.show('Success login', 'success', 5000);
          this.router.navigate(['/']);
        },
        error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
      });
  }
}
