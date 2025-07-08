import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-cookies',
  templateUrl: './cookies.component.html',
  imports: [CommonModule]
})
export class CookiesComponent implements OnInit {
  showCookieConsent = false;

  constructor() { }

  ngOnInit(): void {
    this.showCookieConsent = !localStorage.getItem('cookieConsent');
  }
  acceptCookies(): void {
    localStorage.setItem('cookieConsent', 'accepted');
    this.showCookieConsent = false;
  }

  // loadAnalytics() {
  //   const script = document.createElement('script');
  //   script.src = 'https://www.googletagmanager.com/gtag/js?id=UA-XXXXXXX-X';
  //   script.async = true;
  //   document.head.appendChild(script);

  //   window['dataLayer'] = window['dataLayer'] || [];
  //   function gtag() { window['dataLayer'].push(arguments); }
  //   gtag('js', new Date());
  //   gtag('config', 'UA-XXXXXXX-X');
  // }

  refuseCookies(): void {
    localStorage.setItem('cookieConsent', 'refused');
    this.showCookieConsent = false;
  }
}
