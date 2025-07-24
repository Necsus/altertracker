import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DiscordService } from '../../03_business/discord.service';
import { AuthViewService } from '../../authentication/auth-view.service';

@Component({
  selector: 'app-discord-callback',
  templateUrl: './discord-callback.component.html',
})
export class DiscordCallbackComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private discordService: DiscordService,
    private router: Router,
    private authViewService: AuthViewService
  ) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const code = params['code'];
      if (code) {
        this.discordService.callback$(code)
          .subscribe({
            next: () => {
              this.authViewService.refreshToken();
              setTimeout(() => {
                this.router.navigate(['/me']);
              }, 400);
            },
            error: (err) => {
              console.error('Erreur callback Discord', err);
              this.router.navigate(['/me']);
            }
          });
      }
    });
  }
}