import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FooterComponent } from './shared/footer/footer.component';
import { HeaderComponent } from './shared/header/header.component';
import { LoaderComponent } from './shared/services/loader/loader.component';
import { ToastComponent } from './shared/services/toast/toast.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  imports: [RouterOutlet, ToastComponent, LoaderComponent, HeaderComponent, FooterComponent],
})
export class AppComponent {
}
