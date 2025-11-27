export interface Message {
  id: string;
  type: 'user' | 'bot';
  text: string;
  isTyping?: boolean;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  lastUpdated: number;
}
