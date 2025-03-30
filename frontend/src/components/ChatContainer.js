import React, { useState } from 'react';
import ChatInput from './ChatInput';
import ChatOutput from './ChatOutput';
import "../styles/chatStyling.css";

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false); 

  return (
    <div className="chat-container">
      <div className="chat-box">
        <ChatOutput messages={messages} loading={loading} />
      </div>
      <ChatInput setMessages={setMessages} setLoading={setLoading} />
    </div>
  );
};

export default ChatContainer;
