import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route
          path="/*"
          element={
            <AppLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/financeiro/transacoes" element={<Transactions />} />
                <Route path="/agendamentos" element={<div>Agendamentos - Em breve</div>} />
                <Route path="/relatorios" element={<div>Relatórios - Em breve</div>} />
                <Route path="/configuracoes" element={<div>Configurações - Em breve</div>} />
              </Routes>
            </AppLayout>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
