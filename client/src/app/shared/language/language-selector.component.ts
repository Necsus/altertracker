import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { LanguageService } from './language.service';


@Component({
  selector: 'app-language-selector',
  templateUrl: './language-selector.component.html',
  imports: [TranslateModule, FormsModule],
})
export class LanguageSelectorComponent {
  selectedLanguage!: string;
  constructor(
    private languageService: LanguageService,
    private translate: TranslateService) { }

  ngOnInit(): void {
    const savedLanguage = localStorage.getItem('selectedLanguage');
    const defaultLang = savedLanguage || this.languageService.getCurrentLanguage() || 'fr';

    this.selectedLanguage = defaultLang;
    this.languageService.setLanguage(defaultLang);
    localStorage.setItem('selectedLanguage', defaultLang);
  }

  changeLanguage(event: Event): void {
    const selectedLanguage = (event.target as HTMLSelectElement).value;
    this.languageService.setLanguage(selectedLanguage);
    localStorage.setItem('selectedLanguage', selectedLanguage);
    window.location.reload();
  }
}
