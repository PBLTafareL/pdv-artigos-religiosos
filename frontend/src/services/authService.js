import api from '../api/api'
const authService = {
  login: async (login, password) => {
    const { data } = await api.post('/auth/login/', { login, password })
    localStorage.setItem('access_token',  data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('usuario',       JSON.stringify(data.usuario))
    return data
  },
  logout: async () => {
    try { const r = localStorage.getItem('refresh_token'); if(r) await api.post('/auth/logout/',{refresh:r}) } catch {}
    finally { localStorage.clear() }
  },
  getUsuario: () => { try { return JSON.parse(localStorage.getItem('usuario')) } catch { return null } },
  isAuth: () => !!localStorage.getItem('access_token'),
}
export default authService
