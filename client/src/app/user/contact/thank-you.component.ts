import { Component, Input } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-thank-you',
  templateUrl: './thank-you.component.html',
  imports: [RouterModule],
})
export class ThankYouComponent {
  @Input() context: 'contact' | 'bug' = 'contact';
}