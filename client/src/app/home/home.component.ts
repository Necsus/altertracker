import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  imports: [CommonModule]
})
export class HomeComponent implements OnInit {
  nouvellesCartes = [
    {
      nom: 'Loki',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_COREKS_B_LY_21/UNIQUE/JPG/fr_FR/d2ffe62f5776d6a305d7171b5fd606b8.jpg',
      faction: 'MU',
      type: 'CHARACTER',
      extension: 'COREKS'
    },
    {
      nom: 'Pignon Pugnace',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/05b8de117f0aae34d4209a159311c98e.jpg',
      faction: 'MU',
      type: 'CHARACTER',
      extension: 'COREKS'
    },
    {
      nom: 'Asmodée',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/CORE/CARDS/ALT_CORE_B_LY_20/UNIQUE/JPG/fr_FR/0229edcb3a26cde858d4f87593c34c21.jpg',
      faction: 'BR',
      type: 'CHARACTER',
      extension: 'CORE'
    },
    {
      nom: 'Anansi',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/CORE/CARDS/ALT_CORE_B_LY_13/UNIQUE/JPG/fr_FR/fc21bc5a1f4a434d1fb8ea06356f87e9.jpg',
      faction: 'AX',
      type: 'CHARACTER',
      extension: 'CORE'
    },
    {
      nom: 'Ebenezer Scrooge',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      faction: 'OR',
      type: 'CHARACTER',
      extension: 'ALIZE'
    },
    {
      nom: "Jeanne d'Arc",
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      faction: 'AX',
      type: 'CHARACTER',
      extension: 'COREKS'
    },
    {
      nom: 'Issitoq',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/CORE/CARDS/ALT_CORE_B_OR_19/UNIQUE/JPG/fr_FR/d2895c9cdaa4360e71cc50e144d4f47e.jpg',
      faction: 'OR',
      type: 'CHARACTER',
      extension: 'CORE'
    },
    {
      nom: 'Mécanicienne de la Fonderie',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/CORE/CARDS/ALT_CORE_B_AX_07/UNIQUE/JPG/fr_FR/b3abcc9bced58fc2718abaddb7cacdb6.jpg',
      faction: 'AX',
      type: 'CHARACTER',
      extension: 'CORE'
    },
    {
      nom: 'Porteuse Intrépide',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_AX_37/UNIQUE/JPG/fr_FR/93b09a6ae74dc56299a50cabee961195.jpg',
      faction: 'YZ',
      type: 'CHARACTER',
      extension: 'ALIZE'
    },
    {
      nom: 'Troupière Ordis',
      image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      faction: 'OR',
      type: 'CHARACTER',
      extension: 'COREKS'
    }
  ];

  nouvellesOffres = [
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      vendeur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      vendeur: 'YuGiDealer'
    }
  ];
  offresDisparues = [
    {
      carte: {
        nom: 'Mécanicienne de la Fonderie',
        extension: 'CORE',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/CORE/CARDS/ALT_CORE_B_AX_07/UNIQUE/JPG/fr_FR/b3abcc9bced58fc2718abaddb7cacdb6.jpg',
      },
      prix: 42.00
    },
    {
      carte: {
        nom: 'Porteuse Intrépide',
        extension: 'ALIZE',
        faction: 'YZ',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_AX_37/UNIQUE/JPG/fr_FR/93b09a6ae74dc56299a50cabee961195.jpg',
      },
      prix: 55.50
    }
  ];
  offresModifiees = [
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    },
    {
      carte: {
        nom: 'Troupière Ordis',
        extension: 'COREKS',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_05/UNIQUE/JPG/fr_FR/0917ca0cdfca97b961887782340f2c76.jpg',
      },
      ancienPrix: 80.00,
      nouveauPrix: 69.99,
      vendeur: 'EliteCards'
    },
    {
      carte: {
        nom: 'Pignon Pugnace',
        extension: 'COREKS',
        faction: 'MU',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_MU_20/UNIQUE/JPG/fr_FR/0a622d371f52abbdf6d314de66c09fd7.jpg',
      },
      ancienPrix: 120.00,
      nouveauPrix: 100.00,
      vendeur: 'RetroTCG'
    }
  ];
  nouvellesOffresSite = [
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
    {
      carte: {
        nom: 'Ebenezer Scrooge',
        extension: 'ALIZE',
        faction: 'OR',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/ALIZE/CARDS/ALT_ALIZE_B_OR_37/UNIQUE/JPG/fr_FR/404407f060363a52a3fc85e540696113.jpg',
      },
      prix: 35.00,
      acheteur: 'CarteMania'
    },
    {
      carte: {
        nom: 'Jeanne d\'Arc',
        extension: 'COREKS',
        faction: 'AX',
        image: 'https://altered-prod-eu.s3.amazonaws.com/Art/COREKS/CARDS/ALT_CORE_B_OR_17/UNIQUE/JPG/fr_FR/f69372b8dbfc7bfe8ce9ea8306a4df93.jpg',
      },
      prix: 19.90,
      acheteur: 'YuGiDealer'
    },
  ];
  constructor(private router: Router) { }
  ngOnInit(): void {
    // this.router.navigate(['/cards']);
  }
}
