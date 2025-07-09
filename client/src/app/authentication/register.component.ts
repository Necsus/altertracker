import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../03_business/auth.service';
import { withLoader } from '../shared/services/loader/loader.operator';
import { LoaderService } from '../shared/services/loader/loader.service';
import { ToastService } from '../shared/services/toast/toast.service';
import { AuthViewService } from './auth-view.service';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  imports: [RouterModule, ReactiveFormsModule, TranslateModule]
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
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
    this.registerForm = this.fb.group({
      username: [''],
      email: [''],
      password: ['']
    });
  }

  onSubmit(): void {
    const formValues = this.registerForm.value;
    this.authService.register$(formValues.username, formValues.email, formValues.password)
      .pipe(withLoader(this.loaderService))
      .subscribe({
        next: () => {
          this.router.navigate(['/login']);
        },
        error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
      });
  }
}
