import { Routes } from '@angular/router';
import { AdminGuard } from './00_common/guards/admin.guard';
import { BetaTesterGuard } from './00_common/guards/beta-tester.guard';
import { BgaGuard } from './00_common/guards/bga.guard';
import { noIndexGuard } from './00_common/guards/noindex.guard';
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
import { DeckDetailComponent } from './deck/deck-detail/deck-detail.component';
import { HomeComponent } from './home/home.component';
import { LadderComponent } from './ladder/ladder.component';
import { PlayerComponent } from './ladder/player/player.component';
import { TeamComponent } from './ladder/team/team.component';
import { LegalComponent } from './legal/legal.component';
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
  { path: 'players', component: LadderComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'player/:player_id', component: PlayerComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'team/:team_id', component: TeamComponent, canActivate: [noIndexGuard, BetaTesterGuard] },
  { path: 'deck/:deck_id', component: DeckDetailComponent, canActivate: [noIndexGuard, BgaGuard] },
  { path: 'searches', component: UserSearchesComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'alerts', component: UserAlertsComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'me', component: MeComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'me/discord/link', component: DiscordCallbackComponent, canActivate: [noIndexGuard] },
  { path: 'chat', component: ChatComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'chat/:room_id', component: ChatComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'login', component: LoginComponent, canActivate: [noIndexGuard] },
  { path: 'login-bga', component: LoginBgaComponent, canActivate: [noIndexGuard, BgaGuard] },
  { path: 'register', component: RegisterComponent, canActivate: [noIndexGuard] },
  { path: 'validate-email/:token', component: ValidateEmailComponent, canActivate: [noIndexGuard] },
  { path: 'forgot-password', component: ForgotPasswordComponent, canActivate: [noIndexGuard] },
  { path: 'reset-password/:token', component: ResetPasswordComponent, canActivate: [noIndexGuard] },
  { path: 'articles', component: ArticlesComponent },
  { path: 'article/:id', component: ArticleComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'join-discord', component: JoinDiscordComponent },
  { path: 'about', component: AboutComponent },
  { path: 'policy', component: PolicyComponent },
  { path: 'legal', component: LegalComponent },
  { path: 'cookies', component: CookiesPolicyComponent },
  { path: 'purchase-offers', component: PurchaseOffersComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'collection', component: CollectionComponent, canActivate: [noIndexGuard, TokenGuard] },
  { path: 'admin', component: AdminComponent, canActivate: [noIndexGuard, AdminGuard] },
  { path: 'admin/article/new', component: ArticleEditComponent, canActivate: [noIndexGuard, PublisherGuard] },
  { path: 'admin/article/edit/:id', component: ArticleEditComponent, canActivate: [noIndexGuard, PublisherGuard] },
  { path: 'unauthorized', component: UnauthorizedComponent, canActivate: [noIndexGuard] },
  { path: '**', component: NotFoundComponent, canActivate: [noIndexGuard] }
];
