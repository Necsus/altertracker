import { Directive, HostListener } from '@angular/core';
import { ModalService } from './modal.service';

@Directive({
  selector: '[appModalClose]',
  standalone: true
})
export class ModalCloseDirective {
  constructor(private modalService: ModalService) { }

  @HostListener('click')
  onClick(): void {
    this.modalService.closeAll();
  }
}