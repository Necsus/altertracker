export interface ChatMessage {
  sender: string;
  content: string;
  sent_at: Date;

  formatted_sent_at?: string; // Optional, for formatted display
}
