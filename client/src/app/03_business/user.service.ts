import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { UserSearchModel } from '../01_models/03_business/user-search.model';
import { UserApiService } from '../02_api/user-api.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  constructor(private userApiService: UserApiService) { }
  get_user_searches$(): Observable<UserSearchModel[]> {
    return this.userApiService.get_user_searches$().pipe(map((response: UserSearchModel[]) => {
      return response;
    }));
  }
  post_user_searche$(request: UserSearchModel): Observable<UserSearchModel> {
    return this.userApiService.post_user_searche$(request).pipe(map((response: UserSearchModel) => {
      return response;
    }));
  }
  delete_user_searche$(id_search: number): Observable<void> {
    return this.userApiService.delete_user_searche$(id_search);
  }
}