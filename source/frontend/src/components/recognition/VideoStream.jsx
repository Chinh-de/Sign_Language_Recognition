import React, { useState, useEffect, useRef } from "react";
import axiosInstance from "../../axiosInstance";

// tạm thời bổ sung thêm streamKey để tránh cache, tìm cách xử lí khác sau

const VideoStream = ({ isActive }) => {
  const videoRef = useRef(null);
  const [streamKey, setStreamKey] = useState(Date.now());
  
  useEffect(() => {
    if (isActive) {
      setStreamKey(Date.now());
    }
  }, [isActive]);

  useEffect(() => {
    return () => {
      if (videoRef.current && videoRef.current.src) {
        videoRef.current.src = "";
      }
    };
  }, []);

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg h-full flex flex-col">
      <div className="p-3 bg-gray-700 border-b border-gray-600">
        <h3 className="text-lg font-semibold text-white">Camera Stream</h3>
      </div>
      
      <div className="flex-grow relative overflow-hidden">
        {isActive ? (
          <img
            key={streamKey}
            ref={videoRef}
            src={`${axiosInstance.defaults.baseURL}/recognition/video_feed/?t=${streamKey}`}
            alt="Video Stream"
            className="absolute inset-0 w-full h-full object-contain"
            onError={(e) => {
              console.error("Video stream error:", e);
              setTimeout(() => {
                if (isActive && videoRef.current) {
                  setStreamKey(Date.now());
                }
              }, 2000);
            }}
          />
        ) : (
          <div className="flex items-center justify-center bg-gray-900 absolute inset-0">
            <p className="text-white text-xl">Nhận diện chưa được kích hoạt</p>
          </div>
        )}
      </div>
      
      <div className="p-2 bg-gray-700 text-white text-center border-t border-gray-600">
        <p className="text-sm">{isActive ? "Đang nhận diện..." : "Nhận diện đã dừng"}</p>
      </div>
    </div>
  );
};

export default VideoStream;