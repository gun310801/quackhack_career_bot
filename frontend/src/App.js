import React, { useState } from 'react';
import ChatContainer from './components/ChatContainer';
import './styles/chatStyling.css';

const App = () => {
  const [messages, setMessages] = useState([]);

  return (
    <div>
      <h1 className="app-title">Career Chatbot</h1>
      <ChatContainer messages={messages} setMessages={setMessages} />
    </div>
  );
};

export default App;
