import React, { useState, useRef, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';
import { Message, ChatState } from './types';
import { sendToGemini } from './services/geminiService';

const INITIAL_MESSAGE: Message = {
  id: 'init-1',
  role: 'model',
  text: 'Hello! I am your Groww Mutual Fund assistant. I can help you with details about SBI Mutual Fund schemes. How can I assist you today?',
  timestamp: new Date()
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Auto-scroll to bottom ref
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Create a temporary loading message for better UX
      const loadingId = 'loading-' + Date.now();
      
      // Call Gemini Service
      // We pass the entire history to maintain context
      const responseText = await sendToGemini(text, messages);

      const botMsg: Message = {
        id: loadingId,
        role: 'model',
        text: responseText,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMsg: Message = {
        id: 'error-' + Date.now(),
        role: 'model',
        text: "I'm sorry, I encountered an issue while processing your request. Please try again later.",
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      
      <main className="flex flex-1 overflow-hidden relative">
        {/* Sidebar - Hidden on mobile unless toggled */}
        <div className={`
          absolute inset-y-0 left-0 z-20 w-80 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out
          md:relative md:translate-x-0
          ${sidebarOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full'}
        `}>
          <Sidebar onSelectQuery={handleSendMessage} />
        </div>

        {/* Overlay for mobile sidebar */}
        {sidebarOpen && (
          <div 
            className="absolute inset-0 z-10 bg-black bg-opacity-25 md:hidden"
            onClick={() => setSidebarOpen(false)}
          ></div>
        )}

        {/* Chat Area */}
        <div className="flex-1 flex flex-col h-full w-full bg-slate-50">
          <ChatInterface 
            messages={messages} 
            isLoading={isLoading} 
            onSendMessage={handleSendMessage}
            messagesEndRef={messagesEndRef}
          />
        </div>
      </main>
    </div>
  );
}