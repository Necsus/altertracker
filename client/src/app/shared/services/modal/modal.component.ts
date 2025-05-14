import { AfterViewInit, Component, ComponentRef, Input, Type, ViewChild, ViewContainerRef } from '@angular/core';

@Component({
  selector: 'app-modal',
  templateUrl: './modal.component.html',
  styleUrls: ['modal.component.css'],
  standalone: true
})
export class ModalComponent implements AfterViewInit {
  @Input() component!: Type<any>;
  @Input() inputs?: Record<string, any>;

  @ViewChild('modalContent', { read: ViewContainerRef, static: true })
  modalContent!: ViewContainerRef;

  componentRef!: ComponentRef<any>;

  ngAfterViewInit(): void {
    this.modalContent.clear();
    this.componentRef = this.modalContent.createComponent(this.component);

    if (this.inputs) {
      for (const [key, value] of Object.entries(this.inputs)) {
        this.componentRef.instance[key] = value;
      }
    }
  }

  close(): void {
    // Retirer le composant dynamique
    this.modalContent.clear();
    // Supprimer le fond de la modale
    const modalElement = document.querySelector('.modal');
    if (modalElement) {
      modalElement.remove(); // Si la modale a un conteneur spécifique, on le supprime
    }
    const backdropElement = document.querySelector('.backdrop');
    if (backdropElement) {
      backdropElement.remove(); // Supprimer aussi la superposition grise
    }
  }
}