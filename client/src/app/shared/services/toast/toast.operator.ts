import { tap } from 'rxjs/operators';
import { ToastService, ToastType } from './toast.service';

export function showToast(
  toastService: ToastService,
  message: string,
  type: ToastType = 'success',
  duration: number = 3000
) {
  return tap({
    next: () => toastService.show(message, type, duration),
    error: err => toastService.show(err?.message || 'Erreur', 'error', duration),
  });
}