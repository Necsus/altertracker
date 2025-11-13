import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DeckModel, DeckService } from '../../03_business/deck.service';

@Component({
  selector: 'app-deck-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './deck-detail.component.html',
  styleUrl: './deck-detail.component.css'
})
export class DeckDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly deckService = inject(DeckService);

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

  getCardEntries(): [string, number][] {
    const deck = this.deck();
    if (!deck || !deck.cards_by_uid) return [];
    return Object.entries(deck.cards_by_uid);
  }
}
