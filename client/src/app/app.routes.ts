import { Routes } from '@angular/router';
import { LoginComponent } from './authentication/login.component';
import { TokenComponent } from './authentication/token.component';
import { NotFoundComponent } from './error-pages/not-found/not-found.component';
import { HomeComponent } from './home/home.component';
import { UnderConstructionComponent } from './shared/under-construction/under-construction.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'token', component: TokenComponent },
  { path: 'contact', component: UnderConstructionComponent },
  { path: 'a-propos', component: UnderConstructionComponent },
  { path: 'offres', component: UnderConstructionComponent },
  { path: '**', component: NotFoundComponent }
];
