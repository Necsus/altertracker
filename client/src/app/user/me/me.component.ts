import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-me',
  templateUrl: './me.component.html',
  styleUrls: ['./me.component.css'],
  imports: [FormsModule]
})
export class MeComponent implements OnInit {
  user: any;
  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private toastService: ToastService) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
    });
  }

  updateProfile(): void {
    this.toastService.show('I am under construction', 'error', 5000);
  }

  changePassword(): void {
    this.toastService.show('I am under construction', 'error', 5000);
  }

  deleteAccount(): void {
    this.toastService.show('I am under construction', 'error', 5000);
  }

}
