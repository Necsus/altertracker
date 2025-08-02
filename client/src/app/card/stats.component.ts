import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexDataLabels,
  ApexFill,
  ApexGrid,
  ApexLegend,
  ApexMarkers,
  ApexPlotOptions,
  ApexStroke,
  ApexTooltip,
  ApexXAxis,
  ApexYAxis,
  NgApexchartsModule
} from 'ng-apexcharts';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { OfferPurchase } from '../01_models/03_business/offer-purchase.model';
import { OfferModel } from '../01_models/03_business/offer.model';
import { UserAlertModel } from '../01_models/03_business/user-alert.model';
import { AlteredService } from '../03_business/altered.service';
import { CardService } from '../03_business/card.service';
import { ChatService } from '../03_business/chat.service';
import { UserService } from '../03_business/user.service';
import { AuthViewService } from '../authentication/auth-view.service';
import { IconParserPipe } from '../shared/pipes/icon-parser.pipe';
import { LocalizedValuePipe } from '../shared/pipes/localized-value.pipe';
import { ToDatePipe } from '../shared/pipes/to-date.pipe';
import { PurchaseOfferComponent } from '../shared/purchase-offer/purchase-offer.component';
import { ModalService } from '../shared/services/modal/modal.service';
import { ToastService } from '../shared/services/toast/toast.service';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  dataLabels: ApexDataLabels;
  plotOptions: ApexPlotOptions;
  yAxis: ApexYAxis;
  xAxis: ApexXAxis;
  fill: ApexFill;
  tooltip: ApexTooltip;
  stroke: ApexStroke;
  legend: ApexLegend;
  grid: ApexGrid;
  markers: ApexMarkers;
};

@Component({
  selector: 'app-stats',
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.css'],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    NgApexchartsModule, // Remplace BaseChartDirective
    LocalizedValuePipe,
    TranslateModule,
    IconParserPipe,
    ToDatePipe
  ]
})
export class StatsComponent implements OnInit {
  currentLanguage: string = 'fr';
  reference: string | null = null;
  isLoggedIn: boolean = false;
  searchForm!: FormGroup;
  card!: CardModel | null;
  offers!: OfferModel[] | null;
  purchases!: OfferPurchase[] | null;
  is_favorite: boolean = false;
  is_mine: boolean = false;
  mainCurrency: string = '€';
  chartOptions: Partial<ChartOptions> = {};

  constructor(
    private route: ActivatedRoute,
    private authViewService: AuthViewService,
    private fb: FormBuilder,
    private cardService: CardService,
    private router: Router,
    private userService: UserService,
    private toastService: ToastService,
    private modalService: ModalService,
    private alteredService: AlteredService,
    private chatService: ChatService
  ) { }

  get availableInMarket(): boolean {
    if (this.offers && this.offers.length > 0) {
      return this.offers[0].is_deleted === false;
    }
    return false;
  }

  ngOnInit(): void {
    this.authViewService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
    this.currentLanguage = localStorage.getItem('selectedLanguage') || 'fr';
    this.reference = this.route.snapshot.paramMap.get('reference');
    this.searchForm = this.fb.group({
      reference: [this.reference || ''],
    });
    this.initializeChartOptions();
    if (this.reference) {
      this.loadCardStats(this.reference);
    }
    this.router.events.subscribe(() => {
      window.scrollTo(0, 0);
    });
  }

  isFormValid(): boolean {
    const { reference } = this.searchForm.value;
    return !!(reference);
  }

  onSubmit(): void {
    const reference = this.searchForm.get('reference')?.value;
    this.router.navigate(['/stats', reference]).then(() => {
      window.location.reload();
    });
  }

  loadCardStats(reference: string): void {
    this.cardService.get_card_stats$(reference).subscribe({
      next: (response: { card: CardModel, offers: OfferModel[], purchases: OfferPurchase[], is_mine: boolean }) => {
        this.card = response.card;
        this.is_favorite = !!this.card.alert_id;
        this.offers = response.offers;
        this.prepareChartData();
        this.purchases = response.purchases;
        this.is_mine = response.is_mine;
        this.refreshCardFromAltered();
      },
      error: (err: any) => {
        console.error(err);
        this.card = null;
        this.offers = null;
      }
    });
  }

  formatPrice(value: number, currency: string): string {
    const formattedValue = value.toFixed(2);
    switch (currency) {
      case '$':
      case 'USD':
        return '$' + formattedValue;
      case '€':
      case 'EUR':
        return '€' + formattedValue;
      default:
        return formattedValue + ' ' + currency;
    }
  }

  getCurrencyForDataPoint(index: number): string {
    if (this.offers && this.offers[index]) {
      return this.offers[index].currency || this.mainCurrency;
    }
    return this.mainCurrency;
  }

  detectMainCurrency(): string {
    if (!this.offers || this.offers.length === 0) return '€';

    // Compter les occurrences de chaque devise
    const currencyCount: { [key: string]: number } = {};
    this.offers.forEach(offer => {
      const currency = offer.currency || '€';
      currencyCount[currency] = (currencyCount[currency] || 0) + 1;
    });

    // Retourner la devise la plus fréquente
    return Object.keys(currencyCount).reduce((a, b) =>
      currencyCount[a] > currencyCount[b] ? a : b
    );
  }

  prepareChartData(): void {
    if (this.offers && this.offers.length > 0) {
      // Détecter la devise principale
      this.mainCurrency = this.detectMainCurrency();

      const copiedOffers = this.offers.slice();
      const sortedOffers = copiedOffers.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return dateA - dateB;
      });

      // Préparer les données pour ApexCharts
      const chartData = sortedOffers.map(offer => ({
        x: offer.created_at ? new Date(offer.created_at).getTime() : 0,
        y: offer.price || 0,
        currency: offer.currency || this.mainCurrency // Stocker la devise
      }));

      // Mettre à jour la série du graphique avec le nom de la devise
      this.chartOptions = {
        ...this.chartOptions,
        series: [{
          name: `Prix des offres (${this.mainCurrency})`,
          data: chartData
        }],
        yAxis: {
          ...this.chartOptions.yAxis,
          labels: {
            ...this.chartOptions.yAxis?.labels,
            formatter: (val) => {
              return this.formatPrice(val, this.mainCurrency);
            }
          }
        }
      };
    } else {
      this.chartOptions = {
        ...this.chartOptions,
        series: [{
          name: 'Prix des offres',
          data: []
        }]
      };
    }
  }

  toggleFavorite(): void {
    this.saveFavoriteState();
  }

  saveFavoriteState(): void {
    if (this.card) {
      const reference = this.card.reference;
      const alert_id = this.card.alert_id;
      if (!this.is_favorite && !alert_id) {
        const request = <UserAlertModel>{
          reference_card: reference,
          mail_active: false
        };
        this.userService.post_user_alert$(request).subscribe({
          next: (response: UserAlertModel) => {
            if (this.card) {
              this.is_favorite = !this.is_favorite;
              this.card.alert_id = response.id;
              this.toastService.show(`${reference} ajoutée aux favoris`, 'success', 5000);
            }
          },
          error: (err: any) => {
            this.toastService.show(err.message, 'error', 5000);
          }
        });
      } else {
        if (alert_id) {
          this.userService.delete_user_alert$(alert_id).subscribe({
            next: () => {
              if (this.card) {
                this.is_favorite = !this.is_favorite;
                this.card.alert_id = undefined;
                this.toastService.show(`${reference} supprimée des favoris`, 'success', 5000);
              }
            },
            error: (err: any) => {
              this.toastService.show(err.message, 'error', 5000);
            }
          });
        }
      }
    }
  }

  openPurchaseOfferModal(): void {
    if (this.isLoggedIn) {
      if (this.card) {
        this.modalService.open({
          component: PurchaseOfferComponent,
          inputs: { model: { card: this.card, purchases: this.purchases } }
        });
      } else {
        this.toastService.show('Aucune carte sélectionnée', 'warning', 5000);
      }
    } else {
      this.toastService.show('Veuillez vous connecter pour déposer une offre d\'achat', 'warning', 5000);
    }
  }

  refreshCardFromAltered(): void {
    if (this.card) {
      this.alteredService.getMarketOffer$(this.card).subscribe({
        next: (offer: OfferLiveMarketRequest) => {
          let request = [];
          request.push(offer);
          this.cardService.post_offer_live_market$(request).subscribe({
            next: () => { },
            error: (error) => {
              console.error('Erreur lors de la mise à jour des offres live market :', error);
            }
          });
        }
      });
    }
    if (this.card && (!this.card.image_path_en || !this.card.image_path_en.includes('en_US'))) {
      this.alteredService.getEnglishCardByReference$(this.card).subscribe({
        next: (card: CardModel) => {
          this.card = { ...this.card, ...card };
        },
        complete: () => {
          if (this.card) {
            this.cardService.updateCard$(this.card).subscribe({
              next: (response: any) => {
                console.log(response);
              }
            });
          }
        }
      });
    }
  }

  startChatRoom(offerPurchase: OfferPurchase) {
    this.chatService.create_room$(offerPurchase.id).subscribe({
      next: (room_id: string) => {
        this.router.navigate(['/chat', room_id]);
      },
      error: (err: any) => {
        console.error(err);
        this.toastService.show('Erreur lors de la création de la salle de chat', 'error', 5000);
      }
    });
  }

  private initializeChartOptions(): void {
    this.chartOptions = {
      series: [{
        name: 'Prix des offres',
        data: []
      }],
      chart: {
        type: 'line',
        height: 300,
        background: 'transparent',
        foreColor: '#9ca3af',
        toolbar: {
          show: false
        },
        zoom: {
          enabled: false
        }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth',
        colors: ['#f59e0b'],
        width: 3
      },
      xAxis: {
        type: 'datetime',
        labels: {
          style: {
            colors: '#9ca3af'
          },
          datetimeFormatter: {
            year: 'yyyy',
            month: 'MMM \'yy',
            day: 'dd MMM',
            hour: 'HH:mm'
          }
        },
        axisBorder: {
          color: '#374151'
        },
        axisTicks: {
          color: '#374151'
        }
      },
      yAxis: {
        labels: {
          style: {
            colors: '#9ca3af'
          },
          formatter: (val: number) => {
            return this.formatPrice(val, this.mainCurrency);
          }
        }
      },
      tooltip: {
        theme: 'dark',
        x: {
          format: 'dd/MM/yyyy HH:mm'
        },
        y: {
          formatter: (val: number, opts?: any) => {
            // Utiliser la devise principale par défaut
            return this.formatPrice(val, this.mainCurrency);
          }
        },
        style: {
          fontSize: '12px'
        }
      },
      grid: {
        borderColor: '#374151',
        strokeDashArray: 3,
        xaxis: {
          lines: {
            show: true
          }
        },
        yaxis: {
          lines: {
            show: true
          }
        }
      },
      markers: {
        size: 4,
        colors: ['#f59e0b'],
        strokeColors: '#1f2937',
        strokeWidth: 2,
        hover: {
          size: 6
        }
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'dark',
          gradientToColors: ['#fbbf24'],
          shadeIntensity: 1,
          type: 'horizontal',
          opacityFrom: 0.7,
          opacityTo: 0.3,
          stops: [0, 100]
        }
      },
      legend: {
        show: true,
        position: 'top',
        horizontalAlign: 'left',
        labels: {
          colors: '#9ca3af'
        }
      }
    };
  }
}