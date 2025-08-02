
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
  imports: [FormsModule, NgSelectModule, IconParserPipe, TranslateModule, ModalComponent, ModalCloseDirective],
})
export class EffectBuilderComponent implements OnInit {
  currentLanguage: string = 'fr';
  modalRef?: ComponentRef<any>;
  triggers: EffectModel[] = [];
  conditions: EffectModel[] = [];
  effects: EffectModel[] = [];
  selectedTrigger?: EffectModel | null = null;
  selectedCondition?: EffectModel | null = null;
  selectedEffect?: EffectModel | null = null;
  shortcutTriggers: EffectModel[] = [];

  initialTrigger?: EffectModel | null;
  initialCondition?: EffectModel | null;
  initialEffect?: EffectModel | null;

  // Callback pour récupérer le résultat
  onValidate?: (result: string, trigger: EffectModel | null, condition: EffectModel | null, effect: EffectModel | null) => void;

  constructor(
    private cardService: CardService,
    private translate: TranslateService,
    private modalService: ModalService) {
    this.currentLanguage = this.translate.currentLang || 'en';
    this.translate.onLangChange.subscribe((event) => {
      this.currentLanguage = event.lang;
    });
  }

  ngOnInit(): void {
    this.cardService.getEffect$(this.currentLanguage).subscribe({
      next: (response: EffectModel[]) => {
        this.triggers = [];
        this.conditions = [];
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
        this.setShortcutTriggers();
        this.restoreInitialValues();
      },
      error: (error) => {
        console.error('Error fetching effects:', error);
      }
    });
  }

  // Getter pour l'aperçu en temps réel
  get previewResult(): string {
    const triggerValue = this.selectedTrigger?.value || '';
    const conditionValue = this.selectedCondition?.value || '';
    const effectValue = this.selectedEffect?.value || '';

    let result = '';

    // Construction du résultat
    if (triggerValue) {
      result += triggerValue;
    } else {
      result += '[]';
    }

    if (conditionValue) {
      if (triggerValue) {
        result += ' ';
      }
      result += conditionValue;
    } else {
      if (triggerValue) {
        result += ' ';
      }
      result += '[]';
    }

    if (effectValue) {
      if (conditionValue) {
        result += ' ';
      }
      result += effectValue;
    }

    return result || 'Aucun effet sélectionné';
  }

  // Méthodes pour clear manuellement
  clearTrigger(): void {
    this.selectedTrigger = null;
  }

  clearCondition(): void {
    this.selectedCondition = null;
  }

  clearEffect(): void {
    this.selectedEffect = null;
  }

  selectShortcutTrigger(trigger: EffectModel): void {
    this.selectedTrigger = trigger;
  }

  validate(): void {
    const finalResult = this.previewResult === 'Aucun effet sélectionné' ? '' : this.previewResult;

    // Appeler le callback s'il existe
    if (this.onValidate) {
      this.onValidate(finalResult, this.selectedTrigger ?? null, this.selectedCondition ?? null, this.selectedEffect ?? null);
    }

    this.modalService.closeAll();
  }

  private restoreInitialValues(): void {
    console.log('Restoration des valeurs initiales:', {
      trigger: this.initialTrigger,
      condition: this.initialCondition,
      effect: this.initialEffect
    });

    // Restaurer le trigger
    if (this.initialTrigger) {
      const foundTrigger = this.triggers.find(t => t.id === this.initialTrigger?.id);
      if (foundTrigger) {
        this.selectedTrigger = foundTrigger;
      }
    }

    // Restaurer la condition
    if (this.initialCondition) {
      const foundCondition = this.conditions.find(c => c.id === this.initialCondition?.id);
      if (foundCondition) {
        this.selectedCondition = foundCondition;
      }
    }

    // Restaurer l'effet
    if (this.initialEffect) {
      const foundEffect = this.effects.find(e => e.id === this.initialEffect?.id);
      if (foundEffect) {
        this.selectedEffect = foundEffect;
      }
    }
  }

  private setShortcutTriggers(): void {
    // Définir les IDs ou valeurs des triggers les plus utilisés
    const mostUsedTriggerValues = [
      '{J}',
      '{H}',
      '{R}',
    ];

    this.shortcutTriggers = this.triggers.filter(trigger =>
      mostUsedTriggerValues.some(value =>
        trigger.value.toLowerCase().includes(value.toLowerCase())
      )
    ).slice(0, 3); // Limiter à 4 éléments
  }
}