import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css'
import Recognition from "./page/Recognition.jsx"

function App() {

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Recognition />} />  
        </Routes> 
      </Router> 
    </>
  )
}

export default App
