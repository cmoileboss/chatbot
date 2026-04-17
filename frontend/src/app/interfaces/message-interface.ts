export interface MessageInterface {
  id: number;
  conversationId: number;
  role: 'user' | 'assistant'| 'system';
  content: string;
  timestamp: string;
}