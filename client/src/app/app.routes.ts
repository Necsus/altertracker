import { Routes } from '@angular/router';
import { EndOfServiceComponent } from './end-of-service/end-of-service.component';

export const routes: Routes = [
  // Page de fin de service - toutes les routes redirigent ici
  { path: '', component: EndOfServiceComponent },

  // Toutes les autres routes redirigent vers la page de fin de service
  { path: '**', redirectTo: '', pathMatch: 'full' }
];
