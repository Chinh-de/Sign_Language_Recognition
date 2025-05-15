import React from "react";
import { Link, useLocation } from "react-router-dom";

const Header = () => {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <div className="bg-gray-700 text-white p-3 rounded-lg shadow-md mb-3">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center">
        <div>
          <h2 className="text-xl font-semibold">Nhận diện ngôn ngữ ký hiệu</h2>
          <p className="text-sm text-gray-300">Hệ thống dịch ngôn ngữ ký hiệu thời gian thực</p>
        </div>
        
        <div className="mt-2 sm:mt-0 flex space-x-2">
          <Link 
            to="/" 
            className={`px-4 py-1.5 rounded-lg transition-colors ${
              currentPath === "/" || currentPath === "/recognition"
                ? "bg-blue-600 text-white" 
                : "bg-gray-600 hover:bg-gray-500 text-gray-200"
            }`}
          >
            Nhận diện
          </Link>
          
          <Link 
            to="/dictionary" 
            className={`px-4 py-1.5 rounded-lg transition-colors ${
              currentPath === "/dictionary" 
                ? "bg-blue-600 text-white" 
                : "bg-gray-600 hover:bg-gray-500 text-gray-200"
            }`}
          >
            Từ điển
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Header;