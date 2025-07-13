import { Component } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { CookieConsentService } from '../authentication/cookies/cookies.service';

@Component({
  selector: 'app-cookies-policy',
  templateUrl: './cookies.component.html',
  imports: [TranslateModule],
})
export class CookiesPolicyComponent {
  constructor(private cookieConsentService: CookieConsentService) { }

  openCookieConsent(): void {
    this.cookieConsentService.openConsentPopin();
  }
}
