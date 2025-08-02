
import { Component, OnDestroy, OnInit } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-buymecoffee',
  templateUrl: './buymecoffee.component.html',
  styleUrls: ['./buymecoffee.component.css'],
  imports: [TranslateModule]
})
export class BuyMeCoffeeComponent implements OnInit, OnDestroy {
  showBuyMeACoffeeModal = false;

  private readonly BUYMECOFFEE_NEVER_ASK_KEY = 'buymecoffee_never_ask';
  private readonly BUYMECOFFEE_LAST_SHOWN_KEY = 'buymecoffee_last_shown';

  private modalTimer?: number;
  private readonly SHOW_DELAY = 120000; // 120 secondes
  private readonly REMIND_DELAY = 7 * 24 * 60 * 60 * 1000; // 7 jours

  constructor() { }

  ngOnInit(): void {
    this.scheduleBuyMeACoffeeModal();
  }

  ngOnDestroy(): void {
    if (this.modalTimer) {
      clearTimeout(this.modalTimer);
    }
  }

  private scheduleBuyMeACoffeeModal(): void {
    // Vérifier si l'utilisateur ne veut plus être dérangé
    const neverAsk = localStorage.getItem(this.BUYMECOFFEE_NEVER_ASK_KEY);
    if (neverAsk === 'true') {
      return;
    }

    // Vérifier si on doit respecter un délai
    const lastShown = localStorage.getItem(this.BUYMECOFFEE_LAST_SHOWN_KEY);
    if (lastShown) {
      const lastShownDate = new Date(lastShown);
      const now = new Date();
      const timeDiff = now.getTime() - lastShownDate.getTime();

      if (timeDiff < this.REMIND_DELAY) {
        return; // Pas encore temps de remontrer
      }
    }

    // Programmer l'affichage après le délai
    this.modalTimer = window.setTimeout(() => {
      this.showBuyMeACoffeeModal = true;
      localStorage.setItem(this.BUYMECOFFEE_LAST_SHOWN_KEY, new Date().toISOString());
    }, this.SHOW_DELAY);
  }

  openBuyMeACoffee(): void {
    // Remplace par ton vrai lien Buy Me a Coffee
    window.open('https://buymeacoffee.com/necsus_dev', '_blank', 'noopener,noreferrer');
    this.closeBuyMeACoffeeModal();
  }

  remindLater(): void {
    this.closeBuyMeACoffeeModal();
    // La modal se reaffichera dans 7 jours
  }

  neverAskAgain(): void {
    localStorage.setItem(this.BUYMECOFFEE_NEVER_ASK_KEY, 'true');
    this.closeBuyMeACoffeeModal();
  }

  closeBuyMeACoffeeModal(): void {
    this.showBuyMeACoffeeModal = false;
  }
}
