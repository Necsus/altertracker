import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class CookieConsentService {
  private openConsentSubject = new Subject<void>();
  openConsent$ = this.openConsentSubject.asObservable();

  openConsentPopin() {
    this.openConsentSubject.next();
  }
}