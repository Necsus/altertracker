import { MonoTypeOperatorFunction } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { LoaderService } from './loader.service';

export function withLoader(loaderService: LoaderService): MonoTypeOperatorFunction<any> {
  return (source$) => {
    loaderService.show();
    return source$.pipe(
      finalize(() => loaderService.hide())
    );
  };
}