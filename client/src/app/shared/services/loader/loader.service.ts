import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class LoaderService {
  private _loading = new BehaviorSubject<boolean>(false);
  public readonly loading$ = this._loading.asObservable();

  show(): void {
    this._loading.next(true);
    document.body.style.overflow = 'hidden'; // bloque le scroll
  }

  hide(): void {
    this._loading.next(false);
    document.body.style.overflow = ''; // réactive le scroll
  }
}