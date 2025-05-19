import { Component, OnInit } from '@angular/core';
import { AuthViewService } from '../authentication/auth-view.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  username: string | null = null;
  isAdmin: boolean = false;

  constructor(private authViewService: AuthViewService) { }

  ngOnInit(): void {
    this.username = this.authViewService.getUsername();
    this.isAdmin = this.authViewService.isAdmin();
  }
}