import { inject } from '@angular/core';
import { Meta } from '@angular/platform-browser';
import { CanActivateFn } from '@angular/router';

export const noIndexGuard: CanActivateFn = (route, state) => {
  const meta = inject(Meta);

  // ✅ Ajouter les meta tags de façon discrète
  meta.updateTag({ name: 'robots', content: 'noindex, nofollow' });
  meta.updateTag({ name: 'googlebot', content: 'noindex, nofollow' });

  return true;
};