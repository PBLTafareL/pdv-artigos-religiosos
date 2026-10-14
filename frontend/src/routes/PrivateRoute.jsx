import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function PrivateRoute({ children, perfis = [] }) {
  const { usuario } = useAuth()
  if (!usuario) return <Navigate to="/login" replace />
  if (perfis.length > 0 && !perfis.includes(usuario.perfil)) return <Navigate to="/dashboard" replace />
  return children
}
