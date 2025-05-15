import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import SearchBar from "../components/dictionary/SearchBar";
import WordList from "../components/dictionary/WordList";
import VideoContent from "../components/dictionary/VideoContent";
import VideoPlay from "../components/dictionary/VideoPlay";
import axiosInstance from "../axiosInstance";

const Dictionary = () => {
  const [glosses, setGlosses] = useState([]);
  const [filteredGlosses, setFilteredGlosses] = useState([]);
  const [selectedGloss, setSelectedGloss] = useState(null);
  const [videoSources, setVideoSources] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedVideo, setSelectedVideo] = useState(null);

  useEffect(() => {
    const fetchGlosses = async () => {
      try {
        const response = await axiosInstance.get('/dictionary/glosses/');
        console.log('Glosses fetched:', response.data);
        setGlosses(response.data);
        setFilteredGlosses(response.data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching glosses:', error);
        setIsLoading(false);
      }
    };

    fetchGlosses();
  }, []);

  const handleSearch = (term) => {
    setSearchTerm(term);
    const filtered = glosses.filter(gloss => 
      gloss.toLowerCase().includes(term.toLowerCase())
    );
    setFilteredGlosses(filtered);
  };

  const handleGlossSelect = async (gloss) => {
    setSelectedGloss(gloss);
    setIsLoading(true);
    
    try {
      const response = await axiosInstance.get(`/dictionary/glosses/${gloss}/`);
      setVideoSources(response.data);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching gloss details:', error);
      setIsLoading(false);
    }
  };

  const handleVideoClick = (videoSrc) => {
    setSelectedVideo(videoSrc);
  };

  const handleClosePlay = () => {
    setSelectedVideo(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header component */}
      <Header />
      
      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden p-4">
        <div className="w-1/3 flex flex-col bg-white rounded-lg shadow-md mr-4 overflow-hidden">
          <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Từ điển ngôn ngữ ký hiệu</h2>
            <SearchBar onSearch={handleSearch} />
          </div>
          <div className="flex-1 overflow-auto">
            <WordList 
              glosses={filteredGlosses} 
              selectedGloss={selectedGloss}
              onSelectGloss={handleGlossSelect}
              isLoading={isLoading}
            />
          </div>
        </div>
        
        <div className="w-2/3 bg-white rounded-lg shadow-md overflow-auto">
          <VideoContent
            selectedGloss={selectedGloss}
            videoSources={videoSources}
            isLoading={isLoading}
            onVideoClick={handleVideoClick}
          />
        </div>
      </div>

      {selectedVideo && (
        <VideoPlay videoSrc={selectedVideo} onClose={handleClosePlay} />
      )}
    </div>
  );
};

export default Dictionary;