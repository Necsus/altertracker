import { HttpClient, provideHttpClient } from '@angular/common/http';
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
      provide: LOCALE_ID, useValue: navigator.language
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
