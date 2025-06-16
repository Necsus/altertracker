import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'iconParser' })
export class IconParserPipe implements PipeTransform {
  transform(value: string): string {
    if (!value) return '';
    value = value.replace(/\[\[([^\]]+)\]\]/g, '<b><u>$1</u></b>');
    value = value.replace(/\[([^\]]+)\]/g, '<b>$1</b>');
    // value = value.replace(/(?<!^) \{J\}/g, '<br><i class="altered-icon etb inline-block"></i>');
    // value = value.replace(/(?<!^) \{H\}/g, '<br><i class="altered-icon hand inline-block"></i>');
    // value = value.replace(/(?<!^) \{R\}/g, '<br><i class="altered-icon reserve inline-block"></i>');
    value = value.replace(/\{J\}/gi, '<i class="altered-icon etb inline-block"></i>');
    value = value.replace(/\{H\}/gi, '<i class="altered-icon hand inline-block"></i>');
    value = value.replace(/\{R\}/gi, '<i class="altered-icon reserve inline-block"></i>');
    value = value.replace(/\{T\}/gi, '<i class="altered-icon exhaust inline-block"></i>');
    value = value.replace(/\{D\}/gi, '<i class="altered-icon support inline-block"></i>');
    value = value.replace(/\{I\}/gi, '<i class="altered-icon infinite inline-block"></i>');
    value = value.replace(/\{V\}/gi, '<i class="altered-icon forest inline-block"></i>');
    value = value.replace(/\{M\}/gi, '<i class="altered-icon mountain inline-block"></i>');
    value = value.replace(/\{O\}/gi, '<i class="altered-icon ocean inline-block"></i>');
    value = value.replace(/\{1\}/g, '<i class="altered-icon-basic mana-1 inline-block"></i>');
    value = value.replace(/\{2\}/g, '<i class="altered-icon-basic mana-2 inline-block"></i>');
    value = value.replace(/\{3\}/g, '<i class="altered-icon-basic mana-3 inline-block"></i>');
    value = value.replace(/\{4\}/g, '<i class="altered-icon-basic mana-4 inline-block"></i>');
    value = value.replace(/\{5\}/g, '<i class="altered-icon-basic mana-5 inline-block"></i>');
    value = value.replace(/\{6\}/g, '<i class="altered-icon-basic mana-6 inline-block"></i>');
    value = value.replace(/\{7\}/g, '<i class="altered-icon-basic mana-7 inline-block"></i>');
    value = value.replace(/\{8\}/g, '<i class="altered-icon-basic mana-8 inline-block"></i>');
    value = value.replace(/\{9\}/g, '<i class="altered-icon-basic mana-9 inline-block"></i>');
    value = value.replace(/\[\]/g, '');
    value = value.replace(/  /g, '<br>');
    // value = value.replace(/(?<!^)Lorsque/g, '<br>Lorsque');
    // value = value.replace(/(?<!^)When/g, '<br>When');
    // value = value.replace(/(?<!^)Au Crépuscule\u00A0—/g, '<br>Au Crépuscule\u00A0—');
    // value = value.replace(/(?<!^)At Dusk\u00A0—/g, '<br>At Dusk\u00A0—');
    // value = value.replace(/(?<!^)À la tombée de la Nuit\u00A0—/g, '<br>À la tombée de la Nuit\u00A0—');
    // value = value.replace(/(?<!^)At Night\u00A0—/g, '<br>At Night\u00A0—');
    // value = value.replace(/(?<!^)À Midi\u00A0—/g, '<br>À Midi\u00A0—');
    // value = value.replace(/(?<!^)At Noon\u00A0—/g, '<br>At Noon\u00A0—');
    // value = value.replace(/(?<!^) •/g, '<br>•');

    value = value.replace(/#([^#]+)#/g, '<span class="text-amber-400">$1</span>');

    return value;
  }
}