import { Routes } from '@angular/router';
import { ForgotPasswordComponent } from './authentication/forgot-password.component';
import { LoginComponent } from './authentication/login.component';
import { RegisterComponent } from './authentication/register.component';
import { TokenComponent } from './authentication/token.component';
import { CardsComponent } from './cards/cards.component';
import { ContactComponent } from './contact/contact.component';
import { NotFoundComponent } from './shared/error-pages/not-found/not-found.component';
import { UnderConstructionComponent } from './shared/under-construction/under-construction.component';

export const routes: Routes = [
  { path: '', component: UnderConstructionComponent },
  { path: 'cards', component: CardsComponent },
  { path: 'searchs', component: UnderConstructionComponent },
  { path: 'alerts', component: UnderConstructionComponent },
  { path: 'me', component: UnderConstructionComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'forgotpassword', component: ForgotPasswordComponent },
  { path: 'token', component: TokenComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'about', component: UnderConstructionComponent },
  { path: 'offres', component: UnderConstructionComponent },
  { path: '**', component: NotFoundComponent }
];
