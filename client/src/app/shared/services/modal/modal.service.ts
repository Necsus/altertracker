import { ComponentRef, Injectable, Type, ViewContainerRef } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ModalConfig<T = any> {
  component: Type<T>;
  inputs?: Partial<T>;
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ModalService {
  private modalContainer?: ViewContainerRef;
  private currentModal$ = new BehaviorSubject<ComponentRef<any> | null>(null);
  private keydownListener?: (event: KeyboardEvent) => void;

  setContainer(container: ViewContainerRef): void {
    this.modalContainer = container;
  }

  open<T>(config: ModalConfig<T>): ComponentRef<T> {
    if (!this.modalContainer) {
      throw new Error('Modal container not set. Call setContainer() first.');
    }

    // Fermer la modal existante
    this.closeAll();

    // Créer le composant
    const componentRef = this.modalContainer.createComponent(config.component);

    // Assigner les inputs
    if (config.inputs) {
      Object.assign(componentRef.instance as any, config.inputs);
    }

    // Ajouter les propriétés de configuration à l'instance
    if (componentRef.instance) {
      (componentRef.instance as any)._modalConfig = config;
      (componentRef.instance as any)._modalRef = componentRef;
    }

    this.currentModal$.next(componentRef);

    // Ajouter les event listeners
    this.addEventListeners(componentRef, config);

    return componentRef;
  }

  close(modalRef?: ComponentRef<any>): void {
    const modal = modalRef || this.currentModal$.value;
    if (modal) {
      this.removeEventListeners();
      modal.destroy();
      this.currentModal$.next(null);
    }
  }

  closeAll(): void {
    this.close();
  }

  getCurrentModal(): ComponentRef<any> | null {
    return this.currentModal$.value;
  }

  private addEventListeners(modalRef: ComponentRef<any>, config: ModalConfig): void {
    // Listener pour Escape
    if (config.closeOnEscape !== false) {
      this.keydownListener = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
          this.close(modalRef);
        }
      };
      document.addEventListener('keydown', this.keydownListener);
    }
  }

  private removeEventListeners(): void {
    if (this.keydownListener) {
      document.removeEventListener('keydown', this.keydownListener);
      this.keydownListener = undefined;
    }
  }
}