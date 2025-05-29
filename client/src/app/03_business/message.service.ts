import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { MessageApiService } from '../02_api/message-api.service';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  constructor(private messageApîService: MessageApiService) { }
  get_message_history$(selected_user_id: number): Observable<any> {
    return this.messageApîService.get_message_history$(selected_user_id).pipe(map((dbModel: any) => {
      return dbModel;
    }));
  }
}
