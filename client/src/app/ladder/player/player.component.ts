import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-player',
  templateUrl: './player.component.html',
  imports: []
})
export class PlayerComponent implements OnInit {

  private readonly activatedRoute = inject(ActivatedRoute);

  ngOnInit(): void {
    const player_id = this.activatedRoute.snapshot.paramMap.get('player_id');
    console.log(player_id);
  }
}
