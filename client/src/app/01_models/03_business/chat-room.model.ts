import { ChatMessage } from './chat-message.model';

export interface ChatRoom {
  id: string;
  user1_id: number;
  user2_id: number;
  status: 'active' | 'closed' | 'expired';
  created_at: Date;
  messages: ChatMessage[];

  is_open: boolean;
}
