export interface NewCard {
  name: string,
  image: string,
  faction: string,
  type: string,
  extension: string
}

export interface NewOffer {
  card: NewCard,
  price: number,
  seller: string
}

export interface DeletedOffer {
  card: NewCard,
  price: number
}

export interface EditedOffer {
  card: NewCard,
  oldPrice: number,
  newPrice: number,
  seller: string
}

export interface PurchaseOffer {
  card: NewCard,
  price: number,
  buyer: string
}

export interface HomeViewModel {
  newCards: NewCard[],
  newOffers: NewOffer[],
  deletedOffers: DeletedOffer[],
  editedOffers: EditedOffer[],
  purchaseOffers: PurchaseOffer[]
}