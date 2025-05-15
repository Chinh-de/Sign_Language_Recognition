import React from "react";

const WordList = ({ glosses, selectedGloss, onSelectGloss, isLoading }) => {
  if (isLoading && glosses.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (glosses.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 px-4 text-gray-500 text-center">
        Không tìm thấy từ vựng phù hợp.
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {glosses.map((gloss, index) => (
        <button
          key={index}
          onClick={() => onSelectGloss(gloss)}
          className={`w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors ${
            selectedGloss === gloss ? "bg-blue-50 border-l-4 border-blue-500" : ""
          }`}
        >
          <div className="font-medium">{gloss}</div>
        </button>
      ))}
    </div>
  );
};

export default WordList;