import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Agendamentos from './pages/Agendamentos'
import Relatorios from './pages/Relatorios'
import Configuracoes from './pages/Configuracoes'
import Contas from './pages/Contas'
import Comissoes from './pages/Comissoes'
import Compras from './pages/Compras'
import Cadastros from './pages/Cadastros'
import Marketing from './pages/Marketing'
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
                <Route path="/principal/dashboard" element={<Dashboard />} />
                <Route path="/financeiro/transacoes" element={<Transactions />} />
                <Route path="/financeiro/contas" element={<Contas />} />
                <Route path="/financeiro/comissoes" element={<Comissoes />} />
                <Route path="/agendamentos" element={<Agendamentos />} />
                <Route path="/principal/agendamentos" element={<Agendamentos />} />
                <Route path="/relatorios" element={<Relatorios />} />
                <Route path="/controle/compras" element={<Compras />} />
                <Route path="/cadastro" element={<Cadastros />} />
                <Route path="/marketing" element={<Marketing />} />
                <Route path="/configuracoes" element={<Configuracoes />} />
              </Routes>
            </AppLayout>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
