import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { CardGroupComponent } from '../cards/card-group/card-group.component';
import { SearchPanelComponent } from '../cards/search-panel/search-panel.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  imports: [CommonModule, SearchPanelComponent, CardGroupComponent]
})
export class HomeComponent {

}
