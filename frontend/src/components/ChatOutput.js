import React from 'react';

const ChatOutput = ({ messages }) => {
  return (
    <div className="message-list">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`message ${msg.sender === 'user' ? 'user-message' : 'ai-message'}`}
        >
          <p>{msg.text}</p>
        </div>
      ))}
    </div>
  );
};

export default ChatOutput;
