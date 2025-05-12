import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { LoaderService } from './loader.service';

@Component({
  selector: 'app-loader',
  templateUrl: './loader.component.html',
  imports: [CommonModule]
})
export class LoaderComponent {
  constructor(public loaderService: LoaderService) { }
}
