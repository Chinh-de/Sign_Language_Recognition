import React from "react";
import VideoStream from "./VideoStream";
import RecognitionResults from "./RecognitionResults";

const StreamResult = ({ isActive }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col lg:flex-row gap-1 h-full">
        {/* Camera ở giữa */}
        <div className="lg:w-2/3 h-full flex flex-col">
          <VideoStream isActive={isActive} />
        </div>
        
        {/* Kết quả nhận diện bên phải */}
        <div className="lg:w-1/3 h-full flex">
          <RecognitionResults isActive={isActive} />
        </div>
      </div>
    </div>
  );
};

export default StreamResult;