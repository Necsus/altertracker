import { CardModel } from './card.model';
import { ChatMessage } from './chat-message.model';

export interface ChatRoom {
  id: string;
  reference_card: string;
  card: CardModel;
  seller_id: number;
  buyer_id: number;
  status: 'active' | 'closed' | 'expired';
  created_at: Date;
  messages: ChatMessage;

  is_open: boolean;
}
