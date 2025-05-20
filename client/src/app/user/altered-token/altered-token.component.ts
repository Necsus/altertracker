import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthViewService } from '../../authentication/auth-view.service';
import { ModalService } from '../../shared/services/modal/modal.service';
import { ToastService } from '../../shared/services/toast/toast.service';
import { CguTokenComponent } from './cgu-token.component';

@Component({
  selector: 'app-altered-token',
  templateUrl: './altered-token.component.html',
  imports: [CommonModule, FormsModule]
})
export class AlteredTokenComponent {
  token: string = '';
  acceptedCGU: boolean = false;
  formSubmitted: boolean = false;

  constructor(
    private router: Router,
    private toastService: ToastService,
    private modalService: ModalService,
    private authViewService: AuthViewService) { }

  ngOnInit() {
    this.authViewService.isLoggedIn$.subscribe(status => {
      if (!status) {
        this.router.navigate(['/login']);
      }
    });
    const storedToken = sessionStorage.getItem('altered_token');
    const storedCGU = sessionStorage.getItem('cgu_altered_token');

    if (storedToken) {
      this.token = storedToken;
    }

    if (storedCGU === 'true') {
      this.acceptedCGU = true;
    }
  }

  cguClick(): void {
    this.modalService.open(CguTokenComponent, undefined);
  }

  onSubmit() {
    this.formSubmitted = true;

    if (this.isFormValid()) {
      sessionStorage.setItem('altered_token', this.token);
      sessionStorage.setItem('cgu_altered_token', String(this.acceptedCGU));
      const lastSearchUrl = sessionStorage.getItem('lastSearchUrl');
      this.toastService.show('Token enregistré avec succès', 'success', 5000);
      // Rediriger vers /cards avec les paramètres de recherche si disponibles
      if (lastSearchUrl) {
        this.router.navigateByUrl(lastSearchUrl);
      } else {
        this.router.navigate(['/cards']);
      }
    }
  }

  isFormValid(): boolean {
    return this.acceptedCGU;
  }

  isTokenValid(): boolean {
    // Validation type JWT (3 parties séparées par ".")
    const jwtPattern = /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$/;
    return jwtPattern.test(this.token.trim());
  }
}