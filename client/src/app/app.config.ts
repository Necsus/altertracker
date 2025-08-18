import { registerLocaleData } from '@angular/common';
import { HttpClient, provideHttpClient } from '@angular/common/http';
import localeEn from '@angular/common/locales/en';
import localeFr from '@angular/common/locales/fr';
import { ApplicationConfig, EnvironmentInjector, importProvidersFrom, Injector, LOCALE_ID, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withInMemoryScrolling, withRouterConfig, withViewTransitions } from '@angular/router';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { SocketIoConfig, SocketIoModule } from 'ngx-socket-io';
import { environment } from '../environments/environment';
import { routes } from './app.routes';

const createTranslateLoader = (http: HttpClient): TranslateHttpLoader => {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
};
const config: SocketIoConfig = { url: environment.socketio_url, options: {} };

const browserLang = navigator.language.split('-')[0]; // 'fr' ou 'en'
let navigatorLocale = navigator.language;

switch (browserLang) {
  case 'fr':
    navigatorLocale = 'fr-FR';
    registerLocaleData(localeFr);
    break;
  case 'en':
    navigatorLocale = 'en-US';
    registerLocaleData(localeEn);
    break;
  // Ajoute d'autres cas si besoin
  default:
    navigatorLocale = 'en-US';
    registerLocaleData(localeEn);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(
      routes,
      withRouterConfig({
        onSameUrlNavigation: 'reload'
      }),
      withViewTransitions(),
      withInMemoryScrolling({
        scrollPositionRestoration: 'top'
      })
    ),
    importProvidersFrom(
      TranslateModule.forRoot({
        loader: {
          provide: TranslateLoader,
          useFactory: createTranslateLoader,
          deps: [HttpClient]
        }
      }),
      SocketIoModule.forRoot(config),
    ),
    {
      provide: LOCALE_ID, useValue: navigatorLocale
    },
    provideHttpClient(),
    {
      provide: EnvironmentInjector,
      useFactory: (injector: Injector) => injector.get(EnvironmentInjector),
      deps: [Injector]
    }
  ]
};
