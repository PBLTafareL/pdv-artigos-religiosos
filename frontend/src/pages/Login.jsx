import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
export default function Login() {
  const [login, setLogin] = useState(''); const [pw, setPw] = useState('')
  const { login: doLogin, loading } = useAuth(); const nav = useNavigate()
  const submit = async e => {
    e.preventDefault()
    try { await doLogin(login, pw); nav('/dashboard') }
    catch { toast.error('Login ou senha inválidos.') }
  }
  return (
    <div className="login-wrap">
      <div className="login-card">
        <div style={{ fontSize:52,marginBottom:8 }}>🌸</div>
        <h1>Flor de Dendê PDV</h1>
        <div className="hint">Acesse o painel administrativo</div>
        <form onSubmit={submit}>
          <div className="row">
            <input className="input" type="text" placeholder="E-mail ou nome de usuário"
              value={login} onChange={e=>setLogin(e.target.value)} required autoFocus />
          </div>
          <div className="row">
            <input className="input" type="password" placeholder="Senha"
              value={pw} onChange={e=>setPw(e.target.value)} required />
          </div>
          <div className="row">
            <button type="submit" className="btn btn-primary" style={{ width:'100%',justifyContent:'center' }} disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </div>
        </form>
        <div className="footer">© Flor de Dendê 2026</div>
      </div>
    </div>
  )
}
