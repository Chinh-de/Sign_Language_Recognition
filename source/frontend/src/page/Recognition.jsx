import React, { useState } from "react";
import Sidebar from "../components/recognition/Sidebar";
import StreamResult from "../components/recognition/StreamResult";
import Header from "../components/Header";
import axiosInstance from "../axiosInstance";

const Recognition = () => {
  const [isActive, setIsActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleStartRecognition = async (esp32CamIp, deviceIp) => {
    if (deviceIp === "") deviceIp = "None";
    setIsLoading(true);
    setErrorMessage("");
    
    try {
      const response = await axiosInstance.post("/recognition/control/", {
        esp32CamIp,
        deviceIp,
        action: "start",
      });
      
      if (response.status === 200) {
        setIsActive(true);
        console.log("Recognition started successfully");
      }
    } catch (error) {
      console.error("Error starting recognition:", error);
      setErrorMessage(
        error.response?.data?.error || 
        "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng và thử lại."
      );
      setIsActive(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopRecognition = async () => {
    setIsLoading(true);
    setErrorMessage("");
    
    try {
      const response = await axiosInstance.post("/recognition/control/", {
        action: "stop",
      });
      
      if (response.status === 200) {
        setIsActive(false);
        console.log("Recognition stopped successfully");
      }
    } catch (error) {
      console.error("Error stopping recognition:", error);
      setErrorMessage(
        error.response?.data?.error || 
        "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng và thử lại."
      );
    } finally {
      setIsLoading(false);
    }
  };

return (
    <div className="flex flex-col h-screen overflow-hidden bg-gray-200">
      {/* Header at the top of the page - outside the sidebar/content flex container */}
      <Header />
      
      {/* Main layout container */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          onStartRecognition={handleStartRecognition} 
          onStopRecognition={handleStopRecognition} 
          isActive={isActive} 
        />
        
        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {isLoading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-6 rounded-lg shadow-lg text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-700 mx-auto mb-4"></div>
                <p className="text-lg">Đang xử lý...</p>
              </div>
            </div>
          )}
          
          <div className="p-1 flex flex-col h-full overflow-hidden">
            {errorMessage && (
              <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-3 mb-4">
                <p>{errorMessage}</p>
              </div>
            )}
            
            {/* StreamResult */}
            <div className="flex-1 overflow-hidden">
              <StreamResult isActive={isActive} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Recognition;