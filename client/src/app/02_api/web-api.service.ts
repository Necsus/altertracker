import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError as observableThrowError, of } from 'rxjs';
import { catchError, switchMap, timeout } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { AuthStorageService } from '../00_common/services/auth-storage.service';
import { Exception } from '../01_models/02_api/exeption.model';
import { Param } from '../01_models/02_api/param.model';
import { ExceptionType } from '../01_models/enums/exception-type.enum';
import { ToastService } from '../shared/services/toast/toast.service';

@Injectable({
  providedIn: 'root'
})
export class WebApiService {
  constructor(
    private http: HttpClient,
    private toastService: ToastService,
    private authStorageService: AuthStorageService
  ) { }

  callGet$<Response>(controllerName: string, actionName: string, params: Array<Param> | undefined = undefined,
    timeOutInMillisecond: number = 110000): Observable<Response> {
    const options = this.getOptions(params);
    const url = this.getUrl(controllerName, actionName);
    return this.http.get<Response>(url, options)
      .pipe(
        switchMap((response: any) => {
          if (response?.message) {
            this.toastService.show(response?.message, 'success', 5000);
          }
          return of(response);
        }),
        timeout(timeOutInMillisecond),
        catchError((error: any) => this.handleError$(error))
      );
  }

  callPost$<Response>(controllerName: string, actionName: string, params: Object | undefined = undefined,
    timeOutInMillisecond: number = 110000): Observable<Response> {
    const options = this.getOptions(undefined);
    return this.http.post<Response>(this.getUrl(controllerName, actionName), params, options)
      .pipe(
        switchMap((response: any) => {
          if (response?.message) {
            this.toastService.show(response?.message, 'success', 5000);
          }
          return of(response);
        }),
        timeout(timeOutInMillisecond),
        catchError((error: any) => this.handleError$(error))
      );
  }

  callDelete$<Response>(controllerName: string, actionName: string, params: Array<Param> | undefined = undefined,
    timeOutInMillisecond: number = 110000): Observable<Response> {
    const options = this.getOptions(params);
    return this.http.delete<Response>(this.getUrl(controllerName, actionName), options)
      .pipe(
        switchMap((response: any) => {
          if (response?.message) {
            this.toastService.show(response?.message, 'success', 5000);
          }
          return of(response);
        }),
        timeout(timeOutInMillisecond),
        catchError((error: any) => this.handleError$(error))
      );
  }

  callPut$<Response>(controllerName: string, actionName: string, params: Object | undefined = undefined,
    timeOutInMillisecond: number = 110000): Observable<Response> {
    const options = this.getOptions(undefined);
    return this.http.put<Response>(this.getUrl(controllerName, actionName), params, options)
      .pipe(
        switchMap((response: any) => {
          if (response?.message) {
            this.toastService.show(response?.message, 'success', 5000);
          }
          return of(response);
        }),
        timeout(timeOutInMillisecond),
        catchError((error: any) => this.handleError$(error))
      );
  }

  private getUrl(controllerName: string, actionName: string): string {
    return environment.api_url + '/' + controllerName + '/' + actionName;
  }

  private getOptions(params: Array<Param> | undefined): { headers: HttpHeaders, body: any } {
    let headers = new HttpHeaders();
    headers = headers.set('Accept', 'application/json');

    let token = this.authStorageService.getToken();
    if (token) {
      headers = headers.set('Authorization', 'Bearer ' + token);
      const options = {
        headers: <HttpHeaders>headers, body: <any>null, params: this.convertToParams(params)
      };
      return options;
    }
    const options = { headers: <HttpHeaders>headers, body: <any>null, params: this.convertToParams(params) };
    return options;
  }

  private toISOLocal(d: Date): string {
    const z = (n: number): string => ('0' + n).slice(-2);
    const zz = (n: number): string => ('00' + n).slice(-3);
    let off = d.getTimezoneOffset();
    const sign = off > 0 ? '-' : '+';
    off = Math.abs(off);

    return d.getFullYear() + '-'
      + z(d.getMonth() + 1) + '-' +
      z(d.getDate()) + 'T' +
      z(d.getHours()) + ':' +
      z(d.getMinutes()) + ':' +
      z(d.getSeconds()) + '.' +
      zz(d.getMilliseconds()) +
      sign + z(off / 60 | 0) + ':' + z(off % 60);
  }

  private convertToParams(params: Array<Param> | undefined): HttpParams {
    let queryParams = new HttpParams();
    if (params) {
      for (const param of params) {
        let value = param.value;
        if (value === 0 || value) {
          if (value instanceof Date) {
            value = this.toISOLocal(value as Date);
          }
          queryParams = queryParams.append(param.name, value);
        }
      }
    }
    return queryParams;
  }

  private handleError$(error: HttpErrorResponse | any): Observable<never> {
    const err = new Exception();
    if (error instanceof HttpErrorResponse) {
      switch (error.status) {
        case 401:
          console.log('Vous n\'êtes pas autorisé à effectuer cette action');
          err.type = ExceptionType.Unauthorized;
          break;
        case 417:
          err.type = ExceptionType.ExpectationFailed;
          break;
        case 400:
          err.type = ExceptionType.BadRequest;
          break;
        case 409:
          err.type = ExceptionType.Conflict;
          break;
        case 404:
          err.type = ExceptionType.NotFound;
          break;
        case 500:
          err.type = ExceptionType.InternalServerError;
          break;
        default:
          err.type = ExceptionType.OtherHttpError;
          err.code = error.status.toString();
          break;
      }
      if (error.error && (error.error.message || error.error.msg)) {
        err.message = error.error.message ?? error.error.msg;
      }
    } else {
      err.type = ExceptionType.InternalLocalError;
    }
    err.innerError = error;
    return observableThrowError(() => err);
  }
}
