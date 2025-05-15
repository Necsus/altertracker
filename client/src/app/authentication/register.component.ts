import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../03_business/auth.service';
import { ToastService } from '../shared/services/toast/toast.service';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private toastService: ToastService,
    private router: Router) { }

  ngOnInit(): void {
    this.registerForm = this.fb.group({
      username: [''],
      email: [''],
      password: ['']
    });
  }

  onSubmit(): void {
    const formValues = this.registerForm.value;
    this.authService.register$(formValues.username, formValues.email, formValues.password).subscribe({
      next: (response: any) => {
        console.log(response);
        this.toastService.show('Success register', 'success', 5000);
        this.router.navigate(['/login']);
      },
      error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
    });
  }
}
