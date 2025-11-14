import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'alteredImg' })
export class AlteredImgPipe implements PipeTransform {
  transform(url: string): string {
    if (!url) return '';
    return 'https://www.altered.gg/_next/image?url=' + url.replace(/^\/+/, '') + '&w=640&q=75';
  }
}