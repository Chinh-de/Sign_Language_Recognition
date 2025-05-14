import React, { useRef, useEffect } from 'react';

const StreamResult = ({ sessionId, result, status }) => {
  const videoRef = useRef(null);

  // Thiết lập video stream
  useEffect(() => {
    if (!sessionId || !videoRef.current || status !== 'ONLINE') return;
    
    // Thiết lập nguồn video khi session ONLINE
    videoRef.current.src = `/api/recognition/video_feed/${sessionId}/`;
    
    return () => {
      if (videoRef.current) {
        videoRef.current.src = '';
      }
    };
  }, [sessionId, status]);

  // Hiển thị trạng thái phù hợp
  const renderStatusBadge = () => {
    if (!status) return null;

    let color = 'bg-gray-500';
    let text = 'Unknown';

    switch (status) {
      case 'ONLINE':
        color = 'bg-green-500';
        text = 'Online';
        break;
      case 'BACKGROUND':
        color = 'bg-yellow-500';
        text = 'Chạy ngầm';
        break;
      case 'INACTIVE':
        color = 'bg-red-500';
        text = 'Không hoạt động';
        break;
    }

    return (
      <span className={`${color} text-white text-xs px-2 py-1 rounded-full ml-2`}>
        {text}
      </span>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 bg-black rounded-lg flex items-center justify-center overflow-hidden relative">
        {sessionId && status === 'ONLINE' ? (
          <img
            ref={videoRef}
            className="max-w-full max-h-full object-contain"
            alt="Sign Language Recognition Stream"
          />
        ) : sessionId && status === 'BACKGROUND' ? (
          <div className="text-white text-lg text-center p-8">
            <div className="bg-yellow-500 bg-opacity-20 p-8 rounded-lg">
              <p className="mb-4">Phiên đang chạy ngầm</p>
              <p className="text-sm">Kết quả vẫn được xử lý, nhưng không hiển thị video stream</p>
            </div>
          </div>
        ) : (
          <div className="text-white text-lg text-center p-8">
            Vui lòng nhập IP của ESP32CAM để bắt đầu
          </div>
        )}
        
        {/* Status Indicator */}
        {sessionId && (
          <div className="absolute top-4 right-4">
            {renderStatusBadge()}
          </div>
        )}
      </div>
      
      <div className="mt-4 p-4 bg-white rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2 flex items-center">
          Kết quả nhận diện
        </h3>
        <div className="p-4 bg-gray-100 rounded min-h-[60px] flex items-center text-lg">
          {result || (sessionId ? 'Chờ nhận diện...' : 'Chưa bắt đầu phiên')}
        </div>
      </div>
    </div>
  );
};

export default StreamResult;