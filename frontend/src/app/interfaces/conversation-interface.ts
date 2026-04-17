import { MessageInterface } from "./message-interface";

export interface ConversationInterface {
  id: number;
  user_id: number;
  title: string;
  messages: MessageInterface[];
  createdAt: string;
}