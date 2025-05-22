import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { UserAlertModel } from '../01_models/03_business/user-alert.model';
import { UserContactModel } from '../01_models/03_business/user-contact.model';
import { UserSearchModel } from '../01_models/03_business/user-search.model';
import { WebApiService } from './web-api.service';

@Injectable({
  providedIn: 'root'
})
export class UserApiService {

  private controller = 'user';

  constructor(private wabApiService: WebApiService) {
  }
  count_all_users$(): Observable<any> {
    return this.wabApiService.callGet$(this.controller, 'count');
  }
  get_user_searches$(): Observable<UserSearchModel[]> {
    return this.wabApiService.callGet$(this.controller, 'searches');
  }
  post_user_search$(request: UserSearchModel): Observable<UserSearchModel> {
    return this.wabApiService.callPost$(this.controller, 'searches', request);
  }
  delete_user_search$(id_search: number): Observable<void> {
    return this.wabApiService.callDelete$(this.controller, `searches/${id_search}`);
  }
  get_user_alerts$(): Observable<UserAlertModel[]> {
    return this.wabApiService.callGet$(this.controller, 'alerts');
  }
  post_user_alert$(request: UserAlertModel): Observable<UserAlertModel> {
    return this.wabApiService.callPost$(this.controller, 'alerts', request);
  }
  delete_user_alert$(id_search: number): Observable<void> {
    return this.wabApiService.callDelete$(this.controller, `alerts/${id_search}`);
  }
  put_user_alert$(request: UserAlertModel): Observable<UserAlertModel> {
    return this.wabApiService.callPut$(this.controller, 'alerts', request);
  }
  post_user_contact$(request: UserContactModel): Observable<any> {
    return this.wabApiService.callPost$(this.controller, 'contact', request);
  }
  put_user_username$(request: { new_username: string }): Observable<any> {
    return this.wabApiService.callPut$(this.controller, 'change-username', request);
  }
  put_user_password$(request: { old_password: string, new_password: string }): Observable<any> {
    return this.wabApiService.callPut$(this.controller, 'change-password', request);
  }
  delete_user_account$(request: { password: string }): Observable<any> {
    return this.wabApiService.callPut$(this.controller, 'delete-account', request);
  }
}