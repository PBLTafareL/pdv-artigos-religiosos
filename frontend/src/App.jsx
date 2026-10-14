import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './routes/PrivateRoute'
import Login      from './pages/Login'
import Dashboard  from './pages/Dashboard'
import PDV        from './pages/PDV'
import Products   from './pages/Products'
import Quotations from './pages/Quotations'
import Invoices   from './pages/Invoices'
import Reports    from './pages/Reports'
import Clients    from './pages/Clients'
import Users      from './pages/Users'
import Loyalty    from './pages/Loyalty'

const PR = ({ children, perfis }) => <PrivateRoute perfis={perfis}>{children}</PrivateRoute>

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{ duration:3500 }} />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/"     element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard"  element={<PR perfis={['administrador','funcionario']}><Dashboard /></PR>} />
          <Route path="/pdv"        element={<PR perfis={['administrador','funcionario']}><PDV /></PR>} />
          <Route path="/products"   element={<PR perfis={['administrador','funcionario']}><Products /></PR>} />
          <Route path="/quotations" element={<PR perfis={['administrador','funcionario']}><Quotations /></PR>} />
          <Route path="/invoices"   element={<PR perfis={['administrador','funcionario']}><Invoices /></PR>} />
          <Route path="/reports"    element={<PR perfis={['administrador','funcionario']}><Reports /></PR>} />
          <Route path="/clients"    element={<PR perfis={['administrador','funcionario']}><Clients /></PR>} />
          <Route path="/users"      element={<PR perfis={['administrador']}><Users /></PR>} />
          <Route path="/loyalty"    element={<PR perfis={['administrador','funcionario']}><Loyalty /></PR>} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
