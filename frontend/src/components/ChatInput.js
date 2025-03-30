import React, { useState } from 'react';
import { sendCareerQuery } from '../services/api';

const ChatInput = ({ setMessages }) => {
  const [input, setInput] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Add the user message to the chat
    const userMessage = { sender: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    // Send the query to the backend and get the AI response
    const aiResponse = await sendCareerQuery(input);
    const aiMessage = { sender: 'ai', text: aiResponse };

    // Add the AI message to the chat after the user input
    setMessages((prevMessages) => [...prevMessages, aiMessage]);

    // Clear input after sending
    setInput('');
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
