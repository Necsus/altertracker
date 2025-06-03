import { Pipe, PipeTransform } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Pipe({
  name: 'localizedValue'
})
export class LocalizedValuePipe implements PipeTransform {
  constructor(private translate: TranslateService) { }

  transform(value: any, localizedKey: string, defaultKey: string): any {
    const currentLanguage = this.translate.currentLang || 'fr';
    return currentLanguage === 'en' ? value[localizedKey] : value[defaultKey];
  }
}
