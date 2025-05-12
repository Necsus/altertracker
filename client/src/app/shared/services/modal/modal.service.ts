import { ApplicationRef, ComponentRef, createComponent, EnvironmentInjector, Injectable, Injector, Type } from '@angular/core';
import { ModalComponent } from './modal.component';

@Injectable({
  providedIn: 'root'
})
export class ModalService {
  constructor(
    private appRef: ApplicationRef,
    private injector: Injector,
    private envInjector: EnvironmentInjector) { }

  // Ouverture de la modale avec un composant dynamique
  open<T>(component: Type<T>, inputs?: Partial<T>): ComponentRef<ModalComponent> {
    // Création du composant ModalComponent
    const modalRef = createComponent(ModalComponent, {
      environmentInjector: this.envInjector
    });

    // Affectation du composant dynamique à la modale
    modalRef.instance.component = component;
    modalRef.instance.inputs = inputs;

    // Attacher la vue du modal au DOM
    this.appRef.attachView(modalRef.hostView);
    const domElem = (modalRef.hostView as any).rootNodes[0] as HTMLElement;
    document.body.appendChild(domElem);

    return modalRef;
  }

  // Fermeture de la modale
  close(modalRef: ComponentRef<ModalComponent>) {
    this.appRef.detachView(modalRef.hostView);
    modalRef.destroy();
  }
}