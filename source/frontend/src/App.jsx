import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css'
import Recognition from "./page/Recognition.jsx"
import Dictionary from './page/Dictionary';

function App() {

  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Recognition />} /> 
          <Route path="/dictionary" element={<Dictionary />} /> 
        </Routes> 
      </Router> 
    </>
  )
}

export default App
