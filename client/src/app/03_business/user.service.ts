import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { UserAlertModel } from '../01_models/03_business/user-alert.model';
import { UserContactModel } from '../01_models/03_business/user-contact.model';
import { UserSearchModel } from '../01_models/03_business/user-search.model';
import { UserApiService } from '../02_api/user-api.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  constructor(private userApiService: UserApiService) { }
  count_all_users$(): Observable<number> {
    return this.userApiService.count_all_users$().pipe(map((dbModel: any) => {
      return dbModel.count;
    }));
  }

  get_user_searches$(): Observable<UserSearchModel[]> {
    return this.userApiService.get_user_searches$().pipe(map((response: UserSearchModel[]) => {
      return response;
    }));
  }
  post_user_search$(request: UserSearchModel): Observable<UserSearchModel> {
    return this.userApiService.post_user_search$(request).pipe(map((response: UserSearchModel) => {
      return response;
    }));
  }
  delete_user_search$(id_search: number): Observable<void> {
    return this.userApiService.delete_user_search$(id_search);
  }

  get_user_alerts$(): Observable<UserAlertModel[]> {
    return this.userApiService.get_user_alerts$().pipe(map((response: UserAlertModel[]) => {
      return response;
    }));
  }
  post_user_alert$(request: UserAlertModel): Observable<UserAlertModel> {
    return this.userApiService.post_user_alert$(request).pipe(map((response: UserAlertModel) => {
      return response;
    }));
  }
  delete_user_alert$(id_alert: number): Observable<void> {
    return this.userApiService.delete_user_alert$(id_alert);
  }
  put_user_alert$(request: UserAlertModel): Observable<UserAlertModel> {
    return this.userApiService.put_user_alert$(request).pipe(map((response: UserAlertModel) => {
      return response;
    }));
  }
  post_user_contact$(request: UserContactModel): Observable<UserAlertModel> {
    return this.userApiService.post_user_contact$(request).pipe(map((response: any) => {
      return response;
    }));
  }
  put_user_username$(request: { new_username: string }): Observable<any> {
    return this.userApiService.put_user_username$(request).pipe(map((response: any) => {
      return response;
    }));
  }
  put_user_password$(request: { old_password: string, new_password: string }): Observable<any> {
    return this.userApiService.put_user_password$(request).pipe(map((response: any) => {
      return response;
    }));
  }
  delete_user_account$(request: { password: string }): Observable<any> {
    return this.userApiService.delete_user_account$(request).pipe(map((response: any) => {
      return response;
    }));
  }
  get_user_collection$(): Observable<any> {
    return this.userApiService.get_user_collection$().pipe(map((response: any) => {
      return response;
    }));
  }
  post_user_collection$(request: any): Observable<any> {
    return this.userApiService.post_user_collection$(request).pipe(map((response: any) => {
      return response;
    }));
  }
}