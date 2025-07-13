import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserContactModel } from '../../01_models/03_business/user-contact.model';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ToastService } from '../../shared/services/toast/toast.service';
import { ThankYouComponent } from './thank-you.component';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css'],
  imports: [CommonModule, ReactiveFormsModule, ThankYouComponent]
})
export class ContactComponent implements OnInit {
  contactForm!: FormGroup;
  username: string | null = null;
  messageSended: boolean = false;
  constructor(
    private fb: FormBuilder,
    private toastService: ToastService,
    private authViewService: AuthViewService,
    private userService: UserService,
    private router: Router) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (status) {
        this.username = this.authViewService.getUsername();
      }
    });
    this.contactForm = this.fb.group({
      name: [this.username ?? '', Validators.required],
      email: ['', Validators.required],
      subject: ['', Validators.required],
      message: ['', Validators.required]
    });
  }

  isFormValid(): boolean {
    const { name, email, subject, message } = this.contactForm.value;
    // Vérifie si au moins un champ est rempli ou si forest_power, mountain_power ou ocean_power est égal à 0
    return !!(
      name && email && subject && message
    );
  }

  onSubmit(): void {
    if (!this.isFormValid()) {
      this.toastService.show('Veuillez remplir tous les champs', 'error', 5000);
      return;
    }
    const formValues = this.contactForm.value;
    const request = <UserContactModel>{
      name: formValues.name,
      email: formValues.email,
      subject: formValues.subject,
      message: formValues.message,
    }
    this.userService.post_user_contact$(request).subscribe({
      next: (response: any) => {
        this.messageSended = true;
      },
      error: (err: any) => {
        this.messageSended = false;
      }
    });
  }
}
