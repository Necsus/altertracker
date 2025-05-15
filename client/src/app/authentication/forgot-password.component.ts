import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../03_business/auth.service';
import { ToastService } from '../shared/services/toast/toast.service';


@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class ForgotPasswordComponent implements OnInit {
  forgotPasswordForm!: FormGroup;
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private toastService: ToastService) { }

  ngOnInit(): void {
    this.forgotPasswordForm = this.fb.group({
      email: ['']
    });
  }

  onSubmit(): void {
    const formValues = this.forgotPasswordForm.value;
    this.authService.forgotPassword$(formValues.email).subscribe({
      next: (response: any) => {
        console.log(response);
        this.toastService.show('Password reset email sent!', 'success', 5000)
      },
      error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
    });
  }
}
