import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ToastService } from '../shared/services/toast/toast.service';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  constructor(private fb: FormBuilder, private toastService: ToastService) { }

  ngOnInit(): void {
    this.registerForm = this.fb.group({
      name: [''],
      email: [''],
      password: ['']
    });
  }

  onSubmit(): void {
    this.toastService.show('Fonctionnalité en construction...', 'error', 5000);
  }
}
