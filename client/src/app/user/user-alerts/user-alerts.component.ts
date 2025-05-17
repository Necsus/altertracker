import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserAlertModel } from '../../01_models/03_business/user-alert.model';
import { UserService } from '../../03_business/user.service';
import { CardComponent } from '../../cards/card/card.component';
import { ToastService } from '../../shared/services/toast/toast.service';

@Component({
  selector: 'app-user-alerts',
  templateUrl: './user-alerts.component.html',
  styleUrls: ['./user-alerts.component.css'],
  imports: [CommonModule, CardComponent]
})
export class UserAlertsComponent implements OnInit {
  isLoading: boolean = false; // État de chargement
  alerts: UserAlertModel[] = []; // Liste des recherches

  constructor(
    private userService: UserService,
    private toastService: ToastService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadUserAlerts();
  }

  loadUserAlerts(): void {
    this.isLoading = true; // Démarre le chargement
    this.userService.get_user_alerts$().subscribe({
      next: (response: UserAlertModel[]) => {
        this.alerts = response; // Met à jour la liste des recherches
        this.alerts.map((alert: UserAlertModel) => {
          alert.card.alert_id = alert.id; // Associe l'ID de l'alerte à la carte
        });
      },
      error: (err: any) => {
        this.isLoading = false; // Arrête le chargement
        this.toastService.show(err.message, 'error', 5000);
      },
      complete: () => {
        this.isLoading = false; // Arrête le chargement
      }
    });
  }
}