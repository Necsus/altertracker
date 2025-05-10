import app.data.card_data as card_data

class CardService:
    def get_card_by_reference(reference):
        return card_data.get_card_by_reference(reference)