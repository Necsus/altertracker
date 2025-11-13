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

  getRareCards(): [string, number][] {
    const deck = this.deck();
    if (!deck || !deck.cards_by_uid) return [];
    
    const uniqueCards = deck.unique_cards || [];
    const deckFaction = deck.faction;
    
    return Object.entries(deck.cards_by_uid)
      .filter(([uid, _]) => {
        // Exclure les uniques
        if (uniqueCards.includes(uid)) return false;
        
        // Détecter si c'est une carte rare
        return uid.includes('_R1') || uid.includes('_R2') || uid.endsWith('_R');
      })
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

  /**
   * Obtient l'URL de l'image en gérant automatiquement les variantes R1/R2
   * R1 = in-faction (contient _{FACTION}_)
   * R2 = out-of-faction
   */
  getCardImageUrl(uid: string): string {
    const deck = this.deck();
    if (!deck || !deck.cards_data) return 'assets/images/card-placeholder.png';

    // Chercher d'abord avec l'UID exact
    let cardData = deck.cards_data[uid];
    
    // Si pas trouvé et que c'est une carte rare sans suffixe, chercher la bonne variante
    if (!cardData && uid.endsWith('_R')) {
      const deckFaction = deck.faction;
      
      // Déterminer si la carte est in-faction ou out-of-faction
      const isInFaction = uid.includes(`_${deckFaction}_`);
      
      // Chercher la variante appropriée
      const targetUid = isInFaction ? `${uid}1` : `${uid}2`;
      cardData = deck.cards_data[targetUid];
      
      // Si toujours pas trouvé, essayer l'autre variante
      if (!cardData) {
        const alternateUid = isInFaction ? `${uid}2` : `${uid}1`;
        cardData = deck.cards_data[alternateUid];
      }
    }
    
    // Si toujours pas trouvé et que c'est une variante R1 ou R2, chercher la base
    if (!cardData && (uid.endsWith('_R1') || uid.endsWith('_R2'))) {
      const baseUid = uid.slice(0, -1); // Enlever le 1 ou 2
      cardData = deck.cards_data[baseUid];
    }
    
    return cardData?.imagePath || 'assets/images/card-placeholder.png';
  }

  getCardName(uid: string): string {
    const deck = this.deck();
    if (!deck || !deck.cards_data) return uid;

    // Utiliser la même logique que getCardImageUrl pour trouver les données
    let cardData = deck.cards_data[uid];
    
    if (!cardData && uid.endsWith('_R')) {
      const deckFaction = deck.faction;
      const isInFaction = uid.includes(`_${deckFaction}_`);
      const targetUid = isInFaction ? `${uid}1` : `${uid}2`;
      cardData = deck.cards_data[targetUid];
      
      if (!cardData) {
        const alternateUid = isInFaction ? `${uid}2` : `${uid}1`;
        cardData = deck.cards_data[alternateUid];
      }
    }
    
    if (!cardData && (uid.endsWith('_R1') || uid.endsWith('_R2'))) {
      const baseUid = uid.slice(0, -1);
      cardData = deck.cards_data[baseUid];
    }
    
    return cardData?.name || uid;
  }
}
