import { Component, Input } from '@angular/core';
import { CardModel } from '../../01_models/03_business/card.model';

@Component({
  selector: 'app-card',
  templateUrl: './card.component.html'
})
export class CardComponent {
  @Input() card!: CardModel; // Données de la carte
  isModalOpen = false;
  modalImageSrc = '';

  goToOffer(): void {
    if (this.card.url_offer) {
      window.open(this.card.url_offer, '_blank');
    }
  }

  // refreshPrice(): void {
  //   // Exemple de requête HTTP avec Axios
  //   axios.get(`https://api.altered.gg/cards/${this.card.reference}/offers?itemsPerPage=10&page=1`, {
  //     headers: {
  //       'Authorization': 'Bearer '
  //     }
  //   })
  //     .then(response => {
  //       console.log(response.data);
  //       this.card.price = response.data['hydra:member'][0].convertedPrice;
  //       // Ajoutez ici la logique pour mettre à jour l'affichage du prix
  //     })
  //     .catch(error => {
  //       console.error('Erreur ', error);
  //     });
  // }


  // openModal(imgSrc: string) {
  //   this.modalImageSrc = imgSrc;
  //   this.isModalOpen = true;
  // }

  // closeModal() {
  //   this.isModalOpen = false;
  // }
}
