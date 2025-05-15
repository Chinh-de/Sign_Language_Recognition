import React, { useEffect } from "react";

const VideoPlay = ({ videoSrc, onClose }) => {
  // Close modal with escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  // Close modal if clicking outside the content area
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg w-full max-w-4xl">
        <div className="flex justify-between items-center border-b p-4">
          <h3 className="text-lg font-medium">{videoSrc}</h3>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-4">
          <div className="relative pt-[70%] bg-black">
            <iframe 
              className="absolute inset-0 w-full h-full" 
              allow="autoplay" allowfullscreen
              src={videoSrc}
            >
            </iframe>
          </div>
          
        </div>
        
      </div>
    </div>
  );
};

export default VideoPlay;