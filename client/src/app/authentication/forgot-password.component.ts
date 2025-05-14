import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ToastService } from '../shared/services/toast/toast.service';


@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class ForgotPasswordComponent implements OnInit {
  forgotPasswordForm!: FormGroup;
  constructor(private fb: FormBuilder, private toastService: ToastService) { }

  ngOnInit(): void {
    this.forgotPasswordForm = this.fb.group({
      email: ['']
    });
  }

  onSubmit(): void {
    this.toastService.show('Fonctionnalité en construction...', 'error', 5000);
  }
}
