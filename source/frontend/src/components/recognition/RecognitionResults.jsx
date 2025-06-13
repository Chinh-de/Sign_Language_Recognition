import React, { useState, useEffect, useRef } from "react";
import axiosInstance from "../../axiosInstance";

const RecognitionResults = ({ isActive }) => {
  const [words, setWords] = useState([]);
  const [lastSentence, setLastSentence] = useState("");
  const [isNewSentence, setIsNewSentence] = useState(false);

  const wordListRef = useRef(null);
  const pollingIntervalRef = useRef(null);

  useEffect(() => {
    if (isActive) {
      // Start polling
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const response = await axiosInstance.get("/recognition/poll_result/");
          const data = response.data;

          if (data.has_new) {
            console.log("New data received:", data);
            if (data.index === 0) {
              // hoàn thành một câu, hiển thị kết quả
              setLastSentence(data.text);
              setIsNewSentence(true);

            } else {
              if (isNewSentence) {
                // làm rỗng danh sách từ khi bắt đầu câu mới
                setWords([]);
                setIsNewSentence(false);
              }

              setWords((prevWords) => {
                  return [...prevWords, data.text];
                
              });
            }
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      }, 50); // 0.05 seconds
    }

    return () => {
      // Cleanup
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [isActive, isNewSentence]);

  useEffect(() => {
    if (wordListRef.current) {
      wordListRef.current.scrollTop = wordListRef.current.scrollHeight;
    }
  }, [words]);

  if (!isActive) {
    return (
      <div className="bg-gray-700 rounded-lg flex items-center justify-center w-full h-full">
        <p className="text-white">Bắt đầu nhận diện để xem kết quả</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg flex flex-col w-full h-full">
      <div className="p-3 bg-gray-700 border-b border-gray-600">
        <h3 className="text-lg font-semibold text-white">Kết quả nhận diện</h3>
      </div>
      
      <div className="p-3 flex-grow flex flex-col overflow-hidden">
        <div className="mb-3">
          <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-1">
            Câu nhận dạng được:
          </h4>
          <div className="bg-gray-700 rounded-lg p-3 min-h-[60px] max-h-[80px] flex items-center overflow-auto">
            {lastSentence ? (
              <p className="text-white text-lg">{lastSentence}</p>
            ) : (
              <p className="text-gray-500 italic">Chưa có câu nào được nhận diện</p>
            )}
          </div>
        </div>
        
        <div className="flex-grow flex flex-col min-h-0">
          <h4 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-1">
            Các từ đã nhận diện:
          </h4>
          <div 
            ref={wordListRef}
            className="bg-gray-700 rounded-lg p-3 overflow-y-auto flex-grow"
          >
            {words.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {words.map((word, index) => (
                  <span
                    key={index}
                    className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm"
                  >
                    {word}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">Chưa có từ nào được nhận diện</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecognitionResults;