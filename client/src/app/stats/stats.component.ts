import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferModel } from '../01_models/03_business/offer.model';
import { CardService } from '../03_business/card.service';
import { AuthViewService } from '../authentication/auth-view.service';

@Component({
  selector: 'app-stats',
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.css'],
  imports: [CommonModule, ReactiveFormsModule]
})
export class StatsComponent implements OnInit {
  reference: string | null = null;
  isLoggedIn: boolean = false;
  searchForm!: FormGroup;
  card!: CardModel | null;
  offers!: OfferModel[] | null;

  constructor(
    private route: ActivatedRoute,
    private authViewService: AuthViewService,
    private fb: FormBuilder,
    private cardService: CardService,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
    this.reference = this.route.snapshot.paramMap.get('reference');
    this.searchForm = this.fb.group({
      reference: [this.reference || ''],
    });

    if (this.reference) {
      this.loadCardStats(this.reference);
    }
    // Scroll to top when route changes
    this.router.events.subscribe(() => {
      window.scrollTo(0, 0);
    });
  }

  onSubmit(): void {
    const reference = this.searchForm.get('reference')?.value;
    if (reference) {
      this.router.navigate(['/stats', reference]);
    }
  }

  loadCardStats(reference: string): void {
    this.cardService.get_card_stats$(reference).subscribe({
      next: (response: { card: CardModel, offers: OfferModel[] }) => {
        this.card = response.card;
        this.offers = response.offers;
      },
      error: (err: any) => {
        console.error(err);
        this.card = null;
        this.offers = null;
      }
    });
  }
}
