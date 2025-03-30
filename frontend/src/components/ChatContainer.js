import React from 'react';
import ChatInput from './ChatInput';
import "../styles/chatStyling.css"

const ChatContainer = ({ messages, setMessages }) => {
  return (
    <div className="chat-container">
      <div className="chat-box">
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
      </div>
      <ChatInput setMessages={setMessages} />
    </div>
  );
};

export default ChatContainer;
