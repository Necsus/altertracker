import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SearchFormService {
  formState$ = new BehaviorSubject<any>(null);
  setFormState(state: any) { this.formState$.next(state); }
}