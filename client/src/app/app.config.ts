import { registerLocaleData } from '@angular/common';
import { HttpClient, provideHttpClient } from '@angular/common/http';
import localeEn from '@angular/common/locales/en';
import localeFr from '@angular/common/locales/fr';
import { ApplicationConfig, EnvironmentInjector, importProvidersFrom, Injector, LOCALE_ID, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';
import { SocketIoConfig, SocketIoModule } from 'ngx-socket-io';
import { environment } from '../environments/environment';
import { routes } from './app.routes';

const createTranslateLoader = (http: HttpClient): TranslateHttpLoader => {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
};
const config: SocketIoConfig = { url: environment.socketio_url, options: {} };

const browserLang = navigator.language.split('-')[0]; // 'fr' ou 'en'

switch (browserLang) {
  case 'fr':
    registerLocaleData(localeFr);
    break;
  case 'en':
    registerLocaleData(localeEn);
    break;
  // Ajoute d'autres cas si besoin
  default:
    registerLocaleData(localeEn);
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
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
      provide: LOCALE_ID, useValue: navigator.language.split('-')[0]
    },
    provideHttpClient(),
    {
      provide: EnvironmentInjector,
      useFactory: (injector: Injector) => injector.get(EnvironmentInjector),
      deps: [Injector]
    },
    provideCharts(withDefaultRegisterables())
  ]
};
