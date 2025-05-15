import React from "react";

const VideoContent = ({ selectedGloss, videoSources, isLoading, onVideoClick }) => {
  if (!selectedGloss) {
    return (
      <div className="h-full flex items-center justify-center p-8 text-gray-500">
        <p className="text-center">Vui lòng chọn một từ vựng từ danh sách bên trái để xem video minh họa.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const subsets = Object.keys(videoSources);

  if (subsets.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-8 text-gray-500">
        <p className="text-center">Không có video cho từ vựng này.</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">{selectedGloss}</h2>
      <p className="text-sm text-yellow-800 bg-yellow-100 border border-yellow-300 rounded px-3 py-2 mb-4">
        ⚠ Nếu video không tải được, hãy mở trong tab mới và reload vài lần để Google Drive tạo bản preview.
      </p>      
      {subsets.map((subset) => (
        <div key={subset} className="mb-8">
          <h3 className="text-lg font-semibold mb-4 pb-2 border-b border-gray-200 capitalize">
            {subset === 'train' ? 'Tập huấn luyện' : subset === 'test' ? 'Tập kiểm thử' : 'Tập xác thực'}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {videoSources[subset].map((videoSrc, idx) => (
              <div 
                key={idx} 
                className="border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onVideoClick(videoSrc)}
              >
                <div className="bg-gray-100 p-4 flex items-center justify-center">
                  <div className="relative w-full pt-[56.25%]">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                </div>
                <div className="p-3 bg-white">
                  <p className="text-sm text-gray-700 truncate">{videoSrc.split('/').pop()}</p>
                  <p className="text-xs text-gray-500 mt-1">Nhấp để xem</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default VideoContent;