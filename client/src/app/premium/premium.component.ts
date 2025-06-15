import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-premium',
  templateUrl: './premium.component.html',
  imports: [CommonModule]
})
export class PremiumComponent {

  features = [
    {
      feature: 'Recherche de cartes avancée',
      freemium: true,
      premium: true
    },
    {
      feature: 'Offres d\'achats',
      freemium: true,
      premium: true
    },
    {
      feature: "Historique des offres",
      freemium: 'jusqu\'à 7 jours',
      premium: 'illimité'
    },
    {
      feature: 'Accès aux données journalières',
      freemium: false,
      premium: true
    },
    {
      feature: 'Notifications des offres',
      freemium: '10 cartes',
      premium: 'illimité'
    },
    {
      feature: 'Publicités',
      freemium: 'avec pub',
      premium: 'sans pub'
    },
    {
      feature: 'Cartes similaires',
      freemium: false,
      premium: true
    },
    {
      feature: 'Estimation de prix',
      freemium: false,
      premium: true
    },
    {
      feature: 'Recommandations decks',
      freemium: false,
      premium: true
    },
    {
      feature: 'Prix',
      freemium: 'gratuit',
      premium: '3,99€ / mois'
    }
  ];

}