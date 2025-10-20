import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-team',
  templateUrl: './team.component.html',
  imports: []
})
export class TeamComponent {
  private readonly activatedRoute = inject(ActivatedRoute);

  ngOnInit(): void {
    const team_id = this.activatedRoute.snapshot.paramMap.get('team_id');
    console.log(team_id);
  }
}
