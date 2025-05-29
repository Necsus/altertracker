import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class MessageApiService {

  private controller = 'message';

  constructor(private wabApiService: WebApiService) {
  }
  get_message_history$(selected_user_id: number): Observable<any> {
    return this.wabApiService.callGet$(this.controller, `history/${selected_user_id}`);
  }
}
