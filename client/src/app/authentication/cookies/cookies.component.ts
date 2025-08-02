
import { Component, OnDestroy, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { Subscription } from 'rxjs';
import { CookieConsentService } from './cookies.service';

@Component({
  selector: 'app-cookies',
  templateUrl: './cookies.component.html',
  imports: [TranslateModule]
})
export class CookiesComponent implements OnInit, OnDestroy {
  showCookieConsent = false;
  private sub?: Subscription;

  constructor(private cookieConsentService: CookieConsentService) { }

  ngOnInit(): void {
    this.showCookieConsent = !localStorage.getItem('cookieConsent');
    this.sub = this.cookieConsentService.openConsent$.subscribe(() => {
      this.openConsentPopin();
    });
    if (this.showCookieConsent) {
      this.loadAdsenseScript();
      setTimeout(() => {
        // Recharge les ads après chargement du script
        const ads = document.getElementsByClassName('adsbygoogle');
        for (let i = 0; i < ads.length; i++) {
          try {
            // @ts-ignore
            (window['adsbygoogle'] = window['adsbygoogle'] || []).push({});
          } catch (e) { }
        }
      }, 500);
    }
  }
  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }
  acceptCookies(): void {
    localStorage.setItem('cookieConsent', 'accepted');
    this.showCookieConsent = false;
  }

  loadAdsenseScript() {
    if (document.getElementById('adsbygoogle-js')) return;
    const script = document.createElement('script');
    script.id = 'adsbygoogle-js';
    script.async = true;
    script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4001144292832515';
    script.crossOrigin = 'anonymous';
    document.head.appendChild(script);
  }

  refuseCookies(): void {
    localStorage.setItem('cookieConsent', 'refused');
    this.showCookieConsent = false;
  }

  openConsentPopin(): void {
    console.log('openConsentPopin called');
    this.showCookieConsent = true;
  }
}
