import { AfterViewInit, Component, ViewChild, ViewContainerRef } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthStorageService } from './00_common/services/auth-storage.service';
import { AuthViewService } from './authentication/auth-view.service';
import { ModalService } from './shared/services/modal/modal.service';
// import { CookiesComponent } from './authentication/cookies/cookies.component';
// import { BuyMeCoffeeComponent } from './shared/buymecoffee/buymecoffee.component';
// import { FooterComponent } from './shared/footer/footer.component';
// import { HeaderComponent } from './shared/header/header.component';
// import { LoaderComponent } from './shared/services/loader/loader.component';
// import { ToastComponent } from './shared/services/toast/toast.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  imports: [
    RouterOutlet,
    // ToastComponent,
    // LoaderComponent,
    // HeaderComponent,
    // FooterComponent,
    // CookiesComponent,
    // BuyMeCoffeeComponent
  ],
})
export class AppComponent implements AfterViewInit {
  @ViewChild('modalContainer', { read: ViewContainerRef, static: true })
  modalContainer!: ViewContainerRef;
  constructor(
    private authStorageService: AuthStorageService,
    private authViewService: AuthViewService,
    private modalService: ModalService) { }
  ngAfterViewInit() {
    if (this.modalContainer) {
      this.modalService.setContainer(this.modalContainer);
    }
    const token = this.authStorageService.getToken();
    if (token) {
      this.authViewService.refreshToken();
    } else {
      this.authViewService.loggedIn.next(false); // Assurez-vous de mettre à jour l'état si aucun token n'est présent
    }
  }
}
