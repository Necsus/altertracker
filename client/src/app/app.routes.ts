import { Routes } from '@angular/router';
import { AdminGuard } from './00_common/guards/admin.guard';
import { TokenGuard } from './00_common/guards/token.guard';
import { AboutComponent } from './about/about.component';
import { AdminComponent } from './admin/admin.component';
import { ForgotPasswordComponent } from './authentication/forgot-password/forgot-password.component';
import { LoginComponent } from './authentication/login.component';
import { RegisterComponent } from './authentication/register.component';
import { ResetPasswordComponent } from './authentication/reset-password/reset-password.component';
import { CardsComponent } from './cards/cards.component';
import { HomeComponent } from './home/home.component';
import { NotFoundComponent } from './shared/error-pages/not-found/not-found.component';
import { UnauthorizedComponent } from './shared/error-pages/unauthorized/unauthorized.component';
import { UnderConstructionComponent } from './shared/under-construction/under-construction.component';
import { TokenComponent } from './user/altered-token/token.component';
import { ContactComponent } from './user/contact/contact.component';
import { UserAlertsComponent } from './user/user-alerts/user-alerts.component';
import { UserSearchesComponent } from './user/user-searches/user-searches.component';
import { ValidateEmailComponent } from './user/validate-email/validate-email.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'cards', component: CardsComponent },
  { path: 'searches', component: UserSearchesComponent, canActivate: [TokenGuard] },
  { path: 'alerts', component: UserAlertsComponent, canActivate: [TokenGuard] },
  { path: 'me', component: UnderConstructionComponent, canActivate: [TokenGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'validate-email/:token', component: ValidateEmailComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password/:token', component: ResetPasswordComponent },
  { path: 'token', component: TokenComponent },
  { path: 'contact', component: ContactComponent, canActivate: [TokenGuard] },
  { path: 'about', component: AboutComponent },
  { path: 'purchase-offers', component: UnderConstructionComponent, canActivate: [TokenGuard] },
  { path: 'admin', component: AdminComponent, canActivate: [AdminGuard] },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: '**', component: NotFoundComponent }
];
