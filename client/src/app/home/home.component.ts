import { Component } from '@angular/core';
import { CardGroupComponent } from './card-group/card-group.component';
import { SearchPanelComponent } from './search-panel/search-panel.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  imports: [SearchPanelComponent, CardGroupComponent]
})
export class HomeComponent {
}
