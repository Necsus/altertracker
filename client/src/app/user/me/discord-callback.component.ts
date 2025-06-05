import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DiscordService } from '../../03_business/discord.service';

@Component({
  selector: 'app-discord-callback',
  template: `<p>Connexion Discord en cours...</p>`
})
export class DiscordCallbackComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private discordService: DiscordService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const code = params['code'];
      if (code) {
        this.discordService.callback$(code).subscribe({
          next: () => {
            this.router.navigate(['/me']);
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
