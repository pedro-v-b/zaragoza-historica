import React from 'react';

export const Header: React.FC = () => {
  return (
    <div className="app-header">
      <div className="header-brand">
        <div className="header-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="url(#gradient)"/>
            <path d="M8 22V12L16 8L24 12V22L16 26L8 22Z" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
            <circle cx="16" cy="15" r="3" stroke="white" strokeWidth="1.5"/>
            <path d="M16 18V22" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
            <defs>
              <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                <stop stopColor="#7CA5B8"/>
                <stop offset="1" stopColor="#5A8A9F"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div className="header-text">
          <h1>Zaragoza Historica</h1>
          <p>Explora el patrimonio fotografico de la ciudad</p>
        </div>
      </div>
    </div>
  );
};
