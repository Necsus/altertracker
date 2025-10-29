import { Routes } from '@angular/router';
import { AdminGuard } from './00_common/guards/admin.guard';
import { PublisherGuard } from './00_common/guards/publisher.guard';
import { TokenGuard } from './00_common/guards/token.guard';
import { AboutComponent } from './about/about.component';
import { AdminComponent } from './admin/admin.component';
import { ArticleEditComponent } from './admin/article/article-edit.component';
import { ArticlesComponent } from './article/articles.component';
import { ArticleComponent } from './article/details/article.component';
import { ForgotPasswordComponent } from './authentication/forgot-password/forgot-password.component';
import { LoginBgaComponent } from './authentication/login-bga.component';
import { LoginComponent } from './authentication/login.component';
import { RegisterComponent } from './authentication/register.component';
import { ResetPasswordComponent } from './authentication/reset-password/reset-password.component';
import { StatsComponent } from './card/stats.component';
import { ChatComponent } from './chat/chat.component';
import { HomeComponent } from './home/home.component';
import { LadderComponent } from './ladder/ladder.component';
import { PlayerComponent } from './ladder/player/player.component';
import { TeamComponent } from './ladder/team/team.component';
import { CookiesPolicyComponent } from './policy/cookies.component';
import { PolicyComponent } from './policy/policy.component';
import { CardsComponent } from './search/cards.component';
import { NotFoundComponent } from './shared/error-pages/not-found/not-found.component';
import { UnauthorizedComponent } from './shared/error-pages/unauthorized/unauthorized.component';
import { CollectionComponent } from './user/collection/collection.component';
import { ContactComponent } from './user/contact/contact.component';
import { JoinDiscordComponent } from './user/contact/join-discord.component';
import { DiscordCallbackComponent } from './user/me/discord-callback.component';
import { MeComponent } from './user/me/me.component';
import { PurchaseOffersComponent } from './user/purchase-offers/purchase-offers.component';
import { UserAlertsComponent } from './user/user-alerts/user-alerts.component';
import { UserSearchesComponent } from './user/user-searches/user-searches.component';
import { ValidateEmailComponent } from './user/validate-email/validate-email.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'cards', component: CardsComponent },
  { path: 'stats', component: StatsComponent },
  { path: 'stats/:reference', component: StatsComponent },
  { path: 'players', component: LadderComponent, canActivate: [PublisherGuard] },
  { path: 'player/:player_id', component: PlayerComponent, canActivate: [PublisherGuard] },
  { path: 'team/:team_id', component: TeamComponent, canActivate: [PublisherGuard] },
  { path: 'searches', component: UserSearchesComponent, canActivate: [TokenGuard] },
  { path: 'alerts', component: UserAlertsComponent, canActivate: [TokenGuard] },
  { path: 'me', component: MeComponent, canActivate: [TokenGuard] },
  { path: 'me/discord/link', component: DiscordCallbackComponent },
  { path: 'chat', component: ChatComponent, canActivate: [TokenGuard] },
  { path: 'chat/:room_id', component: ChatComponent, canActivate: [TokenGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'login-bga', component: LoginBgaComponent, canActivate: [AdminGuard] },
  { path: 'register', component: RegisterComponent },
  { path: 'validate-email/:token', component: ValidateEmailComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password/:token', component: ResetPasswordComponent },
  { path: 'articles', component: ArticlesComponent },
  { path: 'article/:id', component: ArticleComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'join-discord', component: JoinDiscordComponent },
  { path: 'about', component: AboutComponent },
  { path: 'policy', component: PolicyComponent },
  { path: 'cookies', component: CookiesPolicyComponent },
  { path: 'purchase-offers', component: PurchaseOffersComponent, canActivate: [TokenGuard] },
  { path: 'collection', component: CollectionComponent, canActivate: [TokenGuard] },
  { path: 'admin', component: AdminComponent, canActivate: [AdminGuard] },
  { path: 'admin/article/new', component: ArticleEditComponent, canActivate: [PublisherGuard] },
  { path: 'admin/article/edit/:id', component: ArticleEditComponent, canActivate: [PublisherGuard] },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: '**', component: NotFoundComponent }
];
