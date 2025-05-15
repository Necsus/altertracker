import { AfterViewInit, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthStorageService } from './00_common/services/auth-storage.service';
import { AuthViewService } from './authentication/auth-view.service';
import { FooterComponent } from './shared/footer/footer.component';
import { HeaderComponent } from './shared/header/header.component';
import { LoaderComponent } from './shared/services/loader/loader.component';
import { ToastComponent } from './shared/services/toast/toast.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  imports: [RouterOutlet, ToastComponent, LoaderComponent, HeaderComponent, FooterComponent],
})
export class AppComponent implements AfterViewInit {
  constructor(private authStorageService: AuthStorageService, private authViewService: AuthViewService) { }
  ngAfterViewInit() {
    if (this.authStorageService.getToken()) {
      this.authViewService['loggedIn'].next(true);
    }
  }
}
