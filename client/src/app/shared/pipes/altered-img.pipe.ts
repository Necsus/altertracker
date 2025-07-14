import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'alteredImg' })
export class AlteredImgPipe implements PipeTransform {
  transform(url: string): string {
    if (!url) return '';
    return 'https://www.altered.gg/cdn-cgi/image/width=384,format=webp,quality=80/' + url.replace(/^\/+/, '');
  }
}