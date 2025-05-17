import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
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
  post_user_searche$(request: UserSearchModel): Observable<UserSearchModel> {
    return this.wabApiService.callPost$(this.controller, 'searches', request);
  }
  delete_user_searche$(id_search: number): Observable<void> {
    return this.wabApiService.callDelete$(this.controller, `searches/${id_search}`);
  }
}