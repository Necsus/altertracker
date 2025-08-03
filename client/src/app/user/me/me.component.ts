import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { environment } from '../../../environments/environment';
import { DiscordService } from '../../03_business/discord.service';
import { UserService } from '../../03_business/user.service';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-me',
  templateUrl: './me.component.html',
  styleUrls: ['./me.component.css'],
  imports: [CommonModule, FormsModule, TranslateModule]
})
export class MeComponent implements OnInit {
  username: string = '';
  oldPassword: string = '';
  newPassword: string = '';
  passwordForDelete: string = '';
  yesIWantToDelete: string = '';
  yesIWantToDeleteValue: string = 'Oui je veux supprimer mon compte';
  discordLinked: boolean = false;
  loadingDiscord: boolean = false;
  constructor(
    private authViewService: AuthViewService,
    private router: Router,
    private toastService: ToastService,
    private userService: UserService,
    private discordService: DiscordService) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) this.router.navigate(['/login']);
      else {
        this.username = this.authViewService.getUsername() ?? '';
        this.discordLinked = this.authViewService.getDiscordIdLinked() ?? false;
      }
    });
  }

  updateProfile(): void {
    if (!this.username || this.username.length < 3) {
      this.toastService.show('Username must be at least 3 characters long', 'error', 5000);
      return;
    }
    this.userService.put_user_username$({ new_username: this.username }).subscribe({
      next: (response) => {
        this.authViewService.refreshToken();
      },
      error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
    });
  }

  linkDiscord() {
    // this.toastService.show('Discord linking is not implemented yet', 'info', 5000);
    if (this.discordLinked || this.loadingDiscord) return;
    this.loadingDiscord = true;
    const discordUrl = `https://discord.com/api/oauth2/authorize?client_id=${environment.discord_client_id}&redirect_uri=${environment.discord_redirect_uri}&response_type=code&scope=identify`;
    // Redirection immédiate : pas besoin de HTTP ici
    window.location.href = discordUrl;
  }

  unlinkDiscord(): void {
    if (!this.discordLinked || this.loadingDiscord) return;

    this.loadingDiscord = true;

    this.discordService.unlink$().subscribe({
      next: () => {
        this.authViewService.refreshToken();
        this.discordLinked = false;
        this.loadingDiscord = false;
      }
    });
  }

  testDiscordMessage(): void {
    this.discordService.test_message$().subscribe({
      next: (response) => {
        this.toastService.show('Discord message test sent', 'success', 5000);
      },
      error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
    });
  }

  changePassword(): void {
    this.userService.put_user_password$({ old_password: this.oldPassword, new_password: this.newPassword }).subscribe({
      next: (response) => {
        this.authViewService.refreshToken();
      },
      error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
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
      },
      error: (err: any) => this.toastService.show(`Error: ${err.message}`, 'error', 5000)
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
