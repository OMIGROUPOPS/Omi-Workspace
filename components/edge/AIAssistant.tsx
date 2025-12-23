'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIAssistantProps {
  gameContext?: {
    homeTeam: string;
    awayTeam: string;
    spread?: number;
    total?: number;
    edge?: number;
  };
}

const SAMPLE_PROMPTS = [
  "Why is the line moving?",
  "Explain the edge on this game",
  "Is there sharp money?",
  "What's the injury report?",
];

export function AIAssistant({ gameContext }: AIAssistantProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateMockResponse(userMessage.content, gameContext),
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };
  
  const handlePromptClick = (prompt: string) => {
    setInput(prompt);
  };
  
  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`
          fixed bottom-6 right-6 z-40 w-14 h-14 
          bg-gradient-to-br from-emerald-500 to-emerald-600 
          rounded-full shadow-lg shadow-emerald-500/25
          flex items-center justify-center
          hover:scale-105 transition-transform
          ${isOpen ? 'hidden' : ''}
        `}
      >
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <span className="absolute w-full h-full rounded-full bg-emerald-500 animate-ping opacity-20"></span>
      </button>
      
      {/* Chat panel */}
      <div
        className={`
          fixed bottom-6 right-6 z-50 w-96 h-[500px] max-h-[80vh]
          bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl
          flex flex-col overflow-hidden
          transform transition-all duration-200 origin-bottom-right
          ${isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0 pointer-events-none'}
        `}
      >
        {/* Header */}
        <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-zinc-100 text-sm">Edge Assistant</h3>
              <p className="text-xs text-zinc-500">AI-powered analysis</p>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1.5 text-zinc-400 hover:text-zinc-100 rounded-lg hover:bg-zinc-700/50 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Context banner */}
        {gameContext && (
          <div className="px-4 py-2 bg-zinc-800/30 border-b border-zinc-800 text-xs">
            <span className="text-zinc-500">Analyzing: </span>
            <span className="text-zinc-300">{gameContext.awayTeam} @ {gameContext.homeTeam}</span>
          </div>
        )}
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-zinc-800 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-zinc-400 text-sm mb-4">Ask me about edges, lines, and betting logic</p>
              
              <div className="space-y-2">
                {SAMPLE_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => handlePromptClick(prompt)}
                    className="block w-full text-left px-3 py-2 text-sm text-zinc-300 bg-zinc-800/50 hover:bg-zinc-800 rounded-lg transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] px-3 py-2 rounded-xl ${
                    msg.role === 'user'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-zinc-800 text-zinc-100'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p className={`text-[10px] mt-1 ${
                    msg.role === 'user' ? 'text-emerald-200' : 'text-zinc-500'
                  }`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-zinc-800 rounded-xl px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-zinc-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about this game..."
              className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </>
  );
}

// Mock response generator (replace with actual AI integration)
function generateMockResponse(question: string, context?: AIAssistantProps['gameContext']): string {
  const q = question.toLowerCase();
  
  if (q.includes('line') && q.includes('mov')) {
    return `The line has moved because of a combination of factors:\n\n1. **Sharp Money**: Early sharp bettors hit the opener hard\n2. **Injury News**: Key player status changed\n3. **Public Betting**: 70% of public bets are on one side\n\nThis 1.5-point move from the opener suggests professional money came in early.`;
  }
  
  if (q.includes('edge')) {
    return `The edge calculation is based on our 5-pillar framework:\n\n• **Execution Risk**: Who decides the outcome\n• **Incentives**: Strategic behavior analysis\n• **Structural Shocks**: Recent news impact\n• **Time Decay**: Timing asymmetries\n• **Flow Analysis**: Sharp vs public money\n\nThe current +2.3% edge indicates the true probability exceeds what the book odds imply.`;
  }
  
  if (q.includes('sharp')) {
    return `Based on line movement patterns:\n\n• Opening line: -3.5\n• Current line: -5\n• Movement: 1.5 points\n\nThis reverse line movement (line moving opposite to public betting %) suggests sharp money came in on the favorite. Typically indicates professional handicappers see value.`;
  }
  
  if (q.includes('injury')) {
    return `I don't have real-time injury data yet, but here's how injuries typically affect edges:\n\n1. **Star Players**: 2-4 point swing on spread\n2. **Key Role Players**: 0.5-1.5 point impact\n3. **Late Scratches**: Often create inefficiencies\n\nCheck the official injury report for the latest updates.`;
  }
  
  return `I can help you analyze:\n\n• Line movement and why lines move\n• Edge calculations and what they mean\n• Sharp vs public money indicators\n• How to interpret our pillar scores\n\nWhat would you like to know more about?`;
}

// Inline chat version for embedding in pages
export function AIAssistantInline({ gameContext }: AIAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateMockResponse(userMessage.content, gameContext),
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };
  
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-zinc-800/50 border-b border-zinc-800 flex items-center gap-2">
        <div className="w-6 h-6 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded flex items-center justify-center">
          <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h3 className="font-semibold text-zinc-100 text-sm">Ask Edge AI</h3>
      </div>
      
      {messages.length > 0 && (
        <div className="max-h-64 overflow-y-auto p-3 space-y-3">
          {messages.map((msg) => (
            <div key={msg.id} className={`${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
              <div className={`inline-block max-w-[90%] px-3 py-2 rounded-lg text-sm ${
                msg.role === 'user' ? 'bg-emerald-600 text-white' : 'bg-zinc-800 text-zinc-100'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-1 px-3">
              <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce"></span>
              <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          )}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="p-3 border-t border-zinc-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Why is the line moving?"
            className="flex-1 bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-emerald-500/50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 text-white text-sm rounded transition-colors"
          >
            Ask
          </button>
        </div>
      </form>
    </div>
  );
}