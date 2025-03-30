import React, { useState } from 'react';
import { sendCareerQuery } from '../services/api';

const ChatInput = ({ setMessages, setLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    
    setLoading(true);

    try {
      const aiResponse = await sendCareerQuery(input);
      const aiMessage = { sender: 'ai', text: aiResponse };

      setMessages((prevMessages) => [...prevMessages, aiMessage]);
    } catch (error) {
      console.error("Error fetching AI response:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input-form">
      <input
        type="text"
        placeholder="Ask a career-related question..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="chat-input"
      />
      <button type="submit" className="send-button">Send</button>
    </form>
  );
};

export default ChatInput;
