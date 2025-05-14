import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ToastService } from '../shared/services/toast/toast.service';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  imports: [RouterModule, ReactiveFormsModule]
})
export class ContactComponent implements OnInit {
  contactForm!: FormGroup;
  constructor(private fb: FormBuilder, private toastService: ToastService) { }

  ngOnInit(): void {
    this.contactForm = this.fb.group({
      name: [''],
      email: [''],
      subject: [''],
      message: ['']
    });
  }

  onSubmit(): void {
    this.toastService.show('Fonctionnalité en construction...', 'error', 5000);
  }
}
