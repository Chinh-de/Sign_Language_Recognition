import React, { useState } from "react";

const Sidebar = ({ onStartRecognition, onStopRecognition, isActive }) => {
  const [esp32CamIp, setEsp32CamIp] = useState("local");
  const [deviceIp, setDeviceIp] = useState("");

  const handleStart = () => {
    onStartRecognition(esp32CamIp, deviceIp);
  };

  const handleStop = () => {
    onStopRecognition();
  };

  return (
    <div className="w-64 bg-gray-800 text-white p-4 shadow-lg">
      <div className="mb-6">
        <h1 className="text-xl font-bold mb-2 mt-20">Nhận diện thủ ngữ</h1>
        <div className="h-1 w-16 bg-blue-500 rounded"></div>
      </div>

      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium">ESP32-CAM IP</label>
        <input
          type="text"
          value={esp32CamIp}
          onChange={(e) => setEsp32CamIp(e.target.value)}
          className="w-full p-2 bg-gray-700 rounded border border-gray-600 text-white"
          placeholder="192.168.1.x hoặc 'local'"
          disabled={isActive}
        />
        <p className="mt-1 text-xs text-gray-400">Nhập 'local' để sử dụng webcam.</p>
      </div>

      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium">Device IP (tùy chọn)</label>
        <input
          type="text"
          value={deviceIp}
          onChange={(e) => setDeviceIp(e.target.value)}
          className="w-full p-2 bg-gray-700 rounded border border-gray-600 text-white"
          placeholder="192.168.1.x hoặc để trống"
          disabled={isActive}
        />
      </div>

      <div className="mt-8">
        {!isActive ? (
          <button
            onClick={handleStart}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition"
          >
            Bắt đầu nhận diện
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition"
          >
            Dừng nhận diện
          </button>
        )}
      </div>
    </div>
  );
};

export default Sidebar;