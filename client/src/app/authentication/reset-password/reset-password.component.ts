import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../03_business/auth.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class ResetPasswordComponent implements OnInit {
  resetPasswordForm!: FormGroup;
  token: string | null = null;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private authService: AuthService,
    private router: Router,
    private toastService: ToastService) { }

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token');
    this.resetPasswordForm = this.fb.group({
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.token) {
      if (this.resetPasswordForm.valid) {
        const { newPassword, confirmPassword } = this.resetPasswordForm.value;
        if (newPassword === confirmPassword) {
          this.authService.resetPassword$(this.token, newPassword).subscribe({
            next: (response: any) => {
              console.log(response);
              this.toastService.show('Password reset successfully', 'success', 5000)
              this.router.navigate(['/login']);
            }
          });
        }
      }
    }
  }
}