export interface Message {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
  isError?: boolean;
}

export interface Scheme {
  id: string;
  name: string;
  category: string;
  risk: 'Low' | 'Moderate' | 'High' | 'Very High';
}

export interface SampleQuery {
  id: string;
  text: string;
  category: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
}