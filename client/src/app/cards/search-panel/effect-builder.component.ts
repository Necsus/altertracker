import { CommonModule } from '@angular/common';
import { Component, ComponentRef, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';
import { TranslateModule } from '@ngx-translate/core';
import { EffectModel } from '../../01_models/03_business/effect.model';
import { CardService } from '../../03_business/card.service';
import { IconParserPipe } from '../../shared/pipes/icon-parser.pipe';

@Component({
  standalone: true,
  selector: 'app-effect-builder',
  templateUrl: './effect-builder.component.html',
  styleUrls: ['./effect-builder.component.css'],
  imports: [CommonModule, FormsModule, NgSelectModule, IconParserPipe, TranslateModule],
})
export class EffectBuilderComponent implements OnInit {
  modalRef?: ComponentRef<any>;
  triggers: EffectModel[] = [];
  conditions: EffectModel[] = [];
  effects: EffectModel[] = [];
  selectedTrigger?: EffectModel;
  selectedCondition?: EffectModel;
  selectedEffect?: EffectModel;
  result: string = '';

  constructor(
    private cardService: CardService) { }

  ngOnInit(): void {
    this.cardService.getEffect$('fr').subscribe({
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
      // Si la précédente est '[]', on ne met pas d'espace
      const joiner = values[i - 1] === '[]' ? '' : ' ';
      result += (values[i] ? joiner + values[i] : '');
    }
    this.result = result;

    if (this.modalRef) {
      this.modalRef.destroy();
    }
  }
}
