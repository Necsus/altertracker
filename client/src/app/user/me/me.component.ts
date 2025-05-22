import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-me',
  templateUrl: './me.component.html',
  styleUrls: ['./me.component.css'],
  imports: [CommonModule, FormsModule]
})
export class MeComponent implements OnInit {
  username: string = '';
  oldPassword: string = '';
  newPassword: string = '';
  passwordForDelete: string = '';
  yesIWantToDelete: string = '';
  yesIWantToDeleteValue: string = 'Oui je veux supprimer mon compte';
  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private toastService: ToastService,
    private userService: UserService) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
      else {
        this.username = this.authViewService.getUsername() ?? '';
      }
    });
  }

  updateProfile(): void {
    if (!this.username || this.username.length < 3) {
      this.toastService.show('Username must be at least 3 characters long', 'error', 5000);
      return;
    }
    this.userService.put_user_username$({ username: this.username }).subscribe({
      next: (response) => {
        console.log(response);
        this.authViewService.logout();
        this.toastService.show('Username updated successfully', 'success', 5000);
      },
      error: (error) => {
        console.error(error);
        this.toastService.show('Error updating username', 'error', 5000);
      }
    });
  }

  changePassword(): void {
    this.userService.put_user_password$({ old_password: '', new_password: '' }).subscribe({
      next: (response) => {
        console.log(response);
        this.toastService.show('Password changed successfully', 'success', 5000);
      }
    });
  }

  deleteAccount(): void {
    if (!this.validateDeleteAccount) {
      this.toastService.show('Please confirm the deletion of your account', 'error', 5000);
      return;
    }
    this.userService.delete_user_account$({ password: this.passwordForDelete }).subscribe({
      next: (response) => {
        console.log(response);
        this.authViewService.logout();
        this.toastService.show('Account deleted successfully', 'success', 5000);
      }
    });
  }

  get validateDeleteAccount(): boolean {
    if (this.yesIWantToDelete === this.yesIWantToDeleteValue
      && this.passwordForDelete && this.passwordForDelete.length > 0) {
      return true;
    }
    return false;
  }
}
