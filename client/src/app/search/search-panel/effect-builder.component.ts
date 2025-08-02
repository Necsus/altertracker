import { CommonModule } from '@angular/common';
import { Component, ComponentRef, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { EffectModel } from '../../01_models/03_business/effect.model';
import { CardService } from '../../03_business/card.service';
import { IconParserPipe } from '../../shared/pipes/icon-parser.pipe';
import { ModalCloseDirective } from '../../shared/services/modal/modal-close.directive';
import { ModalComponent } from '../../shared/services/modal/modal.component';
import { ModalService } from '../../shared/services/modal/modal.service';

@Component({
  selector: 'app-effect-builder',
  templateUrl: './effect-builder.component.html',
  styleUrls: ['./effect-builder.component.css'],
  imports: [CommonModule, FormsModule, NgSelectModule, IconParserPipe, TranslateModule, ModalComponent, ModalCloseDirective],
})
export class EffectBuilderComponent implements OnInit {
  currentLanguage: string = 'fr';
  modalRef?: ComponentRef<any>;
  triggers: EffectModel[] = [];
  conditions: EffectModel[] = [];
  effects: EffectModel[] = [];
  selectedTrigger?: EffectModel;
  selectedCondition?: EffectModel;
  selectedEffect?: EffectModel;
  result: string = '';

  constructor(
    private cardService: CardService,
    private translate: TranslateService,
    private modalService: ModalService) {
    this.currentLanguage = this.translate.currentLang || 'en'; // Définit la langue par défaut
    this.translate.onLangChange.subscribe((event) => {
      this.currentLanguage = event.lang;
    });
  }

  ngOnInit(): void {
    this.cardService.getEffect$(this.currentLanguage).subscribe({
      next: (response: EffectModel[]) => {
        this.triggers = [];
        const nullTrigger = <EffectModel>({
          id: 0,
          type: 'declencheur',
          value: '[]'
        });
        this.triggers.push(nullTrigger);
        this.conditions = [];
        const nullCondition = <EffectModel>({
          id: 0,
          type: 'condition',
          value: '[]'
        });
        this.conditions.push(nullCondition);
        this.effects = [];
        response.forEach((effect: EffectModel) => {
          if (effect.type === 'declencheur') {
            this.triggers.push(effect);
          } else if (effect.type === 'condition') {
            this.conditions.push(effect);
          } else if (effect.type === 'effet') {
            this.effects.push(effect);
          }
        });
      },
      error: (error) => {
        console.error('Error fetching effects:', error);
      }
    });
  }

  validate(): void {
    const values = [
      this.selectedTrigger?.value ?? '[]',
      this.selectedCondition?.value ?? '[]',
      this.selectedEffect?.value ?? ''
    ];

    let result = values[0] || '';
    for (let i = 1; i < values.length; i++) {
      const joiner = values[i - 1] === '[]' ? '' : ' ';
      result += (values[i] ? joiner + values[i] : '');
    }
    this.result = result;

    this.modalService.closeAll();
  }
}
