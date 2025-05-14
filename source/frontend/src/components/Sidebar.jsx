// import React from "react";

// const Sidebar = ({ handleSubmit }) => {
//   return (
//     <div className="w-72 h-full bg-gray-800 text-white p-6 shadow-lg flex flex-col">
//       <h2 className="text-2xl font-bold mb-6 text-center">Sign Language</h2>
//       <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
//         <div>
//           <label htmlFor="ESP32CAM_IP" className="block mb-1">ESP32CAM IP:</label>
//           <input
//             type="text"
//             id="ESP32CAM_IP"
//             name="ESP32CAM_IP"
//             className="w-full px-3 py-2 rounded bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
//             placeholder="IP của ESP32CAM"
//             required
//           />
//         </div>
//         <div>
//           <label htmlFor="device_IP" className="block mb-1">DEVICE IP:</label>
//           <input
//             type="text"
//             id="device_IP"
//             name="device_IP"
//             className="w-full px-3 py-2 rounded bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
//             placeholder="IP của ESP32 thiết bị"
//           />
//         </div>
//         <button
//           type="submit"
//           className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition duration-300"
//         >
//           Bắt đầu nhận diện
//         </button>
//       </form>
//     </div>
//   );
// };

// export default Sidebar;


import React, { useState, useEffect } from 'react';

const Sidebar = ({ handleSubmit, handleStop, loading, sessionActive, sessionStatus }) => {
  const [esp32camIP, setEsp32camIP] = useState(localStorage.getItem('esp32cam_ip') || '');
  const [deviceIP, setDeviceIP] = useState(localStorage.getItem('device_ip') || '');

  // Lưu IP để tiện sử dụng lần sau
  useEffect(() => {
    if (esp32camIP) localStorage.setItem('esp32cam_ip', esp32camIP);
    if (deviceIP) localStorage.setItem('device_ip', deviceIP);
  }, [esp32camIP, deviceIP]);

  // Render trạng thái session
  const renderStatus = () => {
    if (!sessionActive) return <span className="text-gray-300">Chờ kết nối</span>;

    switch (sessionStatus) {
      case 'ONLINE':
        return <span className="text-green-400 font-medium">Đang hoạt động</span>;
      case 'BACKGROUND':
        return <span className="text-yellow-400 font-medium">Đang chạy ngầm</span>;
      case 'INACTIVE':
        return <span className="text-red-400 font-medium">Không hoạt động</span>;
      default:
        return <span className="text-gray-300">Không xác định</span>;
    }
  };

  return (
    <div className="w-80 bg-gray-800 p-6 text-white">
      <h1 className="text-xl font-bold mb-6">🤟 Nhận Diện Ngôn Ngữ Ký Hiệu</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-2 text-sm font-medium">IP ESP32CAM:</label>
          <input
            type="text"
            name="ESP32CAM_IP"
            value={esp32camIP}
            onChange={(e) => setEsp32camIP(e.target.value)}
            placeholder="192.168.1.100"
            className="w-full p-2.5 rounded text-black bg-gray-100"
            required
            disabled={sessionActive || loading}
          />
        </div>
        
        <div>
          <label className="block mb-2 text-sm font-medium">IP ESP32 thiết bị (tùy chọn):</label>
          <input
            type="text"
            name="device_IP"
            value={deviceIP}
            onChange={(e) => setDeviceIP(e.target.value)}
            placeholder="192.168.1.101"
            className="w-full p-2.5 rounded text-black bg-gray-100"
            disabled={sessionActive || loading}
          />
        </div>
        
        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading || sessionActive}
            className={`px-4 py-2.5 rounded font-medium flex-1 ${
              loading || sessionActive 
                ? 'bg-gray-500 cursor-not-allowed' 
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {loading ? 'Đang xử lý...' : '▶️ Bắt đầu'}
          </button>
          
          <button
            type="button"
            onClick={handleStop}
            disabled={loading || !sessionActive}
            className={`px-4 py-2.5 rounded font-medium flex-1 ${
              loading || !sessionActive 
                ? 'bg-gray-500 cursor-not-allowed' 
                : 'bg-red-600 hover:bg-red-700'
            }`}
          >
            ⏹️ Dừng
          </button>
        </div>
      </form>
      
      <div className="mt-6 p-3 bg-gray-700 rounded">
        <h3 className="font-medium mb-2">Trạng thái:</h3>
        <div className="status">
          {renderStatus()}
        </div>
      </div>
      
      {sessionActive && sessionStatus === 'BACKGROUND' && (
        <div className="mt-4 p-3 bg-yellow-800 bg-opacity-50 rounded text-sm">
          <p>⚠️ Phiên đang chạy ngầm</p>
          <p className="mt-1">Kết quả vẫn được xử lý, nhưng không hiển thị video.</p>
        </div>
      )}
    </div>
  );
};

export default Sidebar;