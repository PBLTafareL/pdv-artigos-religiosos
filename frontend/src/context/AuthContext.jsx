import { createContext, useContext, useState } from 'react'
import authService from '../services/authService'
const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(authService.getUsuario())
  const [loading, setLoading] = useState(false)
  const login = async (loginField, password) => {
    setLoading(true)
    try { const d = await authService.login(loginField, password); setUsuario(d.usuario); return d }
    finally { setLoading(false) }
  }
  const logout = async () => { await authService.logout(); setUsuario(null) }
  return (
    <AuthContext.Provider value={{ usuario, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
export const useAuth = () => useContext(AuthContext)
