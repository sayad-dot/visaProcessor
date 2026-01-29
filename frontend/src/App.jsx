import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Container } from '@mui/material'
import Header from './components/Layout/Header'
import Footer from './components/Layout/Footer'
import HomePage from './pages/HomePage'
import NewApplicationPage from './pages/NewApplicationPage'
import ApplicationDetailsPage from './pages/ApplicationDetailsPage'
import './App.css'

function App() {
  return (
    <div className="App">
      <Header />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4, minHeight: 'calc(100vh - 200px)' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/new-application" element={<NewApplicationPage />} />
          <Route path="/application/:id" element={<ApplicationDetailsPage />} />
        </Routes>
      </Container>
      <Footer />
    </div>
  )
}

export default App
