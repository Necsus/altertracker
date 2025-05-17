import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, map, Observable, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { AlteredApiService } from '../02_api/altered-api.service';
import { LoaderService } from '../shared/services/loader/loader.service';

@Injectable({
  providedIn: 'root'
})
export class AlteredService {
  constructor(
    private alteredApiService: AlteredApiService,
    private router: Router,
    private loaderService: LoaderService) { }
  getMarketOffer$(card: CardModel, token: string): Observable<OfferLiveMarketRequest> {
    return this.alteredApiService.getOfferByReference(card.reference, token).pipe(
      map((response: any) => {
        // Mettre à jour les propriétés de la carte avec les données de l'API
        if (response['hydra:totalItems'] && response['hydra:totalItems'] > 0) {
          card.price = Number(response['hydra:member'][0]['convertedPrice']);
          card.url_offer = `https://www.altered.gg/fr-fr/cards/${card.reference}/offers`;

          // Construire et retourner l'objet OfferLiveMarketRequest
          return <OfferLiveMarketRequest>{
            id: 0,
            reference: card.reference,
            status: response['hydra:member'][0]['status'],
            offerId: response['hydra:member'][0]['offerId'],
            convertedPrice: card.price,
            convertedCurrency: response['hydra:member'][0]['convertedCurrency'],
            quantity: response['hydra:member'][0]['quantity'],

          };
        } else {
          card.price = undefined;
          card.url_offer = undefined;

          // Retourner un objet OfferLiveMarketRequest avec un statut non disponible
          return {
            id: 0,
            reference: card.reference,
            status: 'unavailable',
            offerId: undefined,
            convertedPrice: undefined,
            convertedCurrency: undefined,
            quantity: undefined
          };
        }
      }),
      catchError((error) => {
        if (error.status === 401 && error.message == "Expired JWT Token") {
          console.error('Erreur 401 détectée : Redirection vers la page /token.');
          sessionStorage.removeItem('altered_token');
          sessionStorage.removeItem('cgu_altered_token');
          this.loaderService.hide();
          this.router.navigate(['/token']); // Redirige l'utilisateur vers la page /token
          return throwError(() => new Error('Token invalide ou expiré. Veuillez le réinsérer.'));
        }
        return throwError(() => error); // Propager les autres erreurs
      })
    );
  }
}