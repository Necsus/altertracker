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
    // Détecter la langue du navigateur et définir la langue par défaut
    const browserLang = this.translate.getBrowserLang();
    const defaultLang = (browserLang ?? 'fr').match(/en|fr/) ? browserLang ?? 'fr' : 'fr';
    this.selectedLanguage = defaultLang; // Initialiser la langue sélectionnée
    this.languageService.setLanguage(defaultLang);

  }

  changeLanguage(event: Event): void {
    const selectedLanguage = (event.target as HTMLSelectElement).value; // Cast explicite
    this.languageService.setLanguage(selectedLanguage);
  }
}
