import { Injectable } from '@angular/core';
import { catchError, map, Observable, switchMap, throwError } from 'rxjs';
import { OfferLiveMarketRequest } from '../01_models/02_api/card/offer-live-market-request.model';
import { CardModel } from '../01_models/03_business/card.model';
import { AlteredApiService } from '../02_api/altered-api.service';
import { CookieManagerService } from './cookie-manager.service';

@Injectable({
  providedIn: 'root'
})
export class AlteredService {
  constructor(
    private alteredApiService: AlteredApiService,
    private cookieManagerService: CookieManagerService) { }
  getMarketOffer$(card: CardModel): Observable<OfferLiveMarketRequest> {
    return this.cookieManagerService.get_token$().pipe(switchMap((token: any) => {
      if (token) {
        return this.alteredApiService.getOfferByReference$(card.reference, token).pipe(
          map((response: any) => {
            // Mettre à jour les propriétés de la carte avec les données de l'API
            card.price_updated_at = Date.now().toFixed();
            if (response['hydra:totalItems'] && response['hydra:totalItems'] > 0) {
              card.price = Number(response['hydra:member'][0]['price']);
              card.price_currency = response['hydra:member'][0]['currency'];
              card.url_offer = `https://www.altered.gg/fr-fr/cards/${card.reference}/offers`;
              card.visible = true;

              // Construire et retourner l'objet OfferLiveMarketRequest
              return <OfferLiveMarketRequest>{
                reference: card.reference,
                status: response['hydra:member'][0]['status'],
                offerId: response['hydra:member'][0]['offerId'],
                price: card.price,
                currency: response['hydra:member'][0]['currency'],
              };
            } else {
              card.price = undefined;
              card.price_currency = undefined;
              card.url_offer = undefined;
              card.visible = false;

              // Retourner un objet OfferLiveMarketRequest avec un statut non disponible
              return {
                reference: card.reference,
                status: 'unavailable',
                offerId: undefined,
                price: undefined,
                currency: undefined,
              };
            }
          }),
          catchError((error) => {
            if ((error.status === 401 && error.error.message == "Expired JWT Token") || error.status === 500) {
              return this.cookieManagerService.get_token$(true).pipe(
                switchMap((newToken: any) => {
                  if (newToken) {
                    return this.alteredApiService.getOfferByReference$(card.reference, newToken);
                  } else {
                    return throwError(() => new Error('Impossible de recharger le token.'));
                  }
                })
              );
            }
            return throwError(() => error); // Propager les autres erreurs
          })
        );
      } else {
        // Si le token n'est pas disponible, retourner un objet OfferLiveMarketRequest avec un statut non disponible
        return throwError(() => new Error('Token non disponible'));
      }
    }));
  }
  getEnglishCardByReference$(card: CardModel): Observable<CardModel> {
    return this.alteredApiService.getCardByReferenceEnglish$(card.reference).pipe(
      map((response: any) => {
        // Mettre à jour les propriétés de la carte avec les données de l'API
        if (response['cardType']) {
          card.image_path_en = response['allImagePath']['en-us'] ?? null;
          card.main_effect_en = response['elements']['MAIN_EFFECT'] ?? null;
          card.echo_effect_en = response['elements']['ECHO_EFFECT'] ?? null;
        }

        return card; // Retourner la carte mise à jour
      }),
      catchError((error) => {
        if ((error.status === 401 && error.error.message == "Expired JWT Token") || error.status === 500) {
          return throwError(() => new Error('Token invalide ou expiré. Veuillez le réinsérer.'));
        }
        return throwError(() => error); // Propager les autres erreurs
      }));
  }
  getCollection$(token: string, page: number): Observable<any> {
    return this.alteredApiService.getCollection$(token, page).pipe(
      map((response: any) => {
        if (response && response['hydra:totalItems'] > 0) {
          return response; // Retourner la collection
        } else {
          throw new Error('Collection vide ou non trouvée');
        }
      }),
      catchError((error) => {
        if ((error.status === 401 && error.error.message == "Expired JWT Token") || error.status === 500) {
          return throwError(() => new Error('Token invalide ou expiré. Veuillez le réinsérer.'));
        }
        return throwError(() => error); // Propager les autres erreurs
      })
    );
  }
}
