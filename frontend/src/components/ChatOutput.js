import React from 'react';

const ChatOutput = ({ messages, loading }) => {
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
            {/* {loading && (
                <div className="loading-indicator">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                </div>
            )} */}
            {loading && (
                <div className="loading-duck">
                    <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmJjdmhzbXIzM3drNmNtcTgzOXNmb2FxODJrbjJsbjIyMG1lZWZ3ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/vIJaz7nMJhTUc/giphy.gif" alt="Loading..." />
                </div>
            )}
        </div>
    );
};

export default ChatOutput;
