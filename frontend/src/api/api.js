import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
}, err => Promise.reject(err))

api.interceptors.response.use(
  res => res,
  async err => {
    const orig = err.config
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('no refresh')
        const { data } = await axios.post('/api/auth/refresh/', { refresh })
        localStorage.setItem('access_token', data.access)
        orig.headers.Authorization = `Bearer ${data.access}`
        return api(orig)
      } catch {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
