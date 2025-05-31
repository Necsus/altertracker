import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  constructor(private translate: TranslateService) {
    const browserLang = translate.getBrowserLang() || 'fr';
    translate.use(browserLang.match(/en|fr/) ? browserLang : 'en'); // Définit la langue par défaut
  }

  setLanguage(lang: string): void {
    this.translate.use(lang);
  }

  getCurrentLanguage(): string {
    return this.translate.currentLang;
  }
}
