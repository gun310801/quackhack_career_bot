import React, { useState } from 'react';
import ChatInput from './ChatInput';
import ChatOutput from './ChatOutput';
import "../styles/chatStyling.css";

const EdaGraph = ({ filename }) => {
  return (
    <iframe
      src={`/eda_graphs/${filename}`} 
      width="100%"
      height="500px"
      style={{ border: "none" }}
      title="EDA Graph"
    />
  );
};

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showGraph, setShowGraph] = useState(false); 
  const [graphFilename, setGraphFilename] = useState('boxplot_salary_level.html'); 

  const toggleGraphDisplay = () => {
    setShowGraph(!showGraph);
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        <ChatOutput messages={messages} loading={loading} />
      </div>

      <button onClick={toggleGraphDisplay} className="toggle-graph-button">
        {showGraph ? 'Hide Graph' : 'Show Graph'}
      </button>

      {showGraph && (
        <EdaGraph filename={graphFilename} />
      )}

      <ChatInput setMessages={setMessages} setLoading={setLoading} />
    </div>
  );
};

export default ChatContainer;


