import { Routes } from '@angular/router';
import { TokenGuard } from './00_common/guards/token.guard';
import { ForgotPasswordComponent } from './authentication/forgot-password.component';
import { LoginComponent } from './authentication/login.component';
import { RegisterComponent } from './authentication/register.component';
import { TokenComponent } from './authentication/token.component';
import { CardsComponent } from './cards/cards.component';
import { ContactComponent } from './contact/contact.component';
import { HomeComponent } from './home/home.component';
import { NotFoundComponent } from './shared/error-pages/not-found/not-found.component';
import { UnderConstructionComponent } from './shared/under-construction/under-construction.component';
import { UserSearchesComponent } from './user-searches/user-searches.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'cards', component: CardsComponent },
  { path: 'searches', component: UserSearchesComponent, canActivate: [TokenGuard] },
  { path: 'alerts', component: UnderConstructionComponent, canActivate: [TokenGuard] },
  { path: 'me', component: UnderConstructionComponent, canActivate: [TokenGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'forgotpassword', component: ForgotPasswordComponent },
  { path: 'token', component: TokenComponent },
  { path: 'contact', component: ContactComponent, canActivate: [TokenGuard] },
  { path: 'about', component: UnderConstructionComponent },
  { path: 'purchaseoffers', component: UnderConstructionComponent, canActivate: [TokenGuard] },
  { path: '**', component: NotFoundComponent }
];
