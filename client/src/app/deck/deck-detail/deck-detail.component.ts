import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CardModel } from '../../01_models/03_business/card.model';
import { DeckModel, DeckService } from '../../03_business/deck.service';
import { CardImgComponent } from '../../search/card/card-img.component';
import { AlteredImgPipe } from '../../shared/pipes/altered-img.pipe';
import { LocalizedValuePipe } from '../../shared/pipes/localized-value.pipe';
import { ModalService } from '../../shared/services/modal/modal.service';

@Component({
  selector: 'app-deck-detail',
  standalone: true,
  imports: [CommonModule, TranslateModule, LocalizedValuePipe, AlteredImgPipe],
  templateUrl: './deck-detail.component.html'
})
export class DeckDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly deckService = inject(DeckService);
  private readonly translate = inject(TranslateService);
  private readonly modalService = inject(ModalService);

  deck = signal<DeckModel | null>(null);
  isLoading = signal(true);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const deckId = this.route.snapshot.paramMap.get('deck_id');
    if (deckId) {
      this.loadDeck(deckId);
    } else {
      this.error.set('ID du deck manquant');
      this.isLoading.set(false);
    }
  }

  private loadDeck(deckId: string): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.deckService.get_deck$(deckId, true).subscribe({
      next: (deck: DeckModel) => {
        this.deck.set(deck);
        this.isLoading.set(false);
      },
      error: (error) => {
        this.error.set(error.message || 'Erreur de chargement du deck');
        this.isLoading.set(false);
      }
    });
  }

  openModal(card: CardModel): void {
    const currentLanguage = this.translate.currentLang || 'fr';
    this.modalService.open({
      component: CardImgComponent,
      inputs: { src: currentLanguage === 'en' ? card.image_path_en : card.imagePath },
      closeOnBackdrop: true,
      closeOnEscape: true
    });
  }

  goToStats(reference: string): void {
    const url = this.router.createUrlTree(['/stats', reference]).toString();
    window.open(url, '_blank');
  }

  getFactionColor(faction: string): string {
    const colors: { [key: string]: string } = {
      'AX': 'blue',
      'BR': 'red',
      'LY': 'purple',
      'MU': 'green',
      'OR': 'yellow',
      'YZ': 'indigo'
    };
    return colors[faction] || 'gray';
  }

  getRareCards(): [string, number][] {
    const deck = this.deck();
    if (!deck || !deck.cards_by_uid) return [];

    const uniqueCards = deck.unique_cards || [];

    return Object.entries(deck.cards_by_uid)
      .filter(([uid, _]) => !uniqueCards.includes(uid) && (uid.includes('_R1') || uid.includes('_R2') || uid.endsWith('_R')))
      .sort((a, b) => a[0].localeCompare(b[0]));
  }

  getCommonCards(): [string, number][] {
    const deck = this.deck();
    if (!deck || !deck.cards_by_uid) return [];

    const uniqueCards = deck.unique_cards || [];

    return Object.entries(deck.cards_by_uid)
      .filter(([uid, _]) => {
        // Exclure les uniques
        if (uniqueCards.includes(uid)) return false;

        // Exclure les rares (_R, _R1, _R2)
        if (uid.includes('_R1') || uid.includes('_R2') || uid.endsWith('_R')) return false;

        // Inclure seulement les communes (_C)
        return uid.endsWith('_C');
      })
      .sort((a, b) => a[0].localeCompare(b[0]));
  }

  getCardImageUrl(uid: string): string {
    const deck = this.deck();
    if (!deck || !deck.cards_data) return 'assets/images/card-placeholder.png';

    const cardData = deck.cards_data[uid];
    return cardData?.imagePath || 'assets/images/card-placeholder.png';
  }

  getCardName(uid: string): string {
    const deck = this.deck();
    if (!deck || !deck.cards_data) return uid;

    const cardData = deck.cards_data[uid];
    return cardData?.name || uid;
  }

  getCard(uid: string): CardModel | null {
    const deck = this.deck();
    if (!deck || !deck.cards_data) return null;

    const cardData = deck.cards_data[uid];
    return cardData ?? null;
  }
}
