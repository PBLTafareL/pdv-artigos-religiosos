import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

const VAZIO = { nome:'', username:'', email:'', password:'', confirmar_senha:'', telefone:'', cpf:'', perfil:'funcionario' }

export default function Users() {
  const [users, setUsers]     = useState([])
  const [loading, setLoading] = useState(true)
  const [show, setShow]       = useState(false)
  const [editando, setEditando] = useState(null)
  const [form, setForm]       = useState(VAZIO)
  const f = k => e => setForm(p=>({...p,[k]:e.target.value}))

  const carregar = async () => {
    try { const {data}=await api.get('/auth/users/'); setUsers(data.resultados||[]) }
    catch { toast.error('Erro') } finally { setLoading(false) }
  }
  useEffect(()=>{ carregar() },[])

  const abrirNovo = () => { setEditando(null); setForm(VAZIO); setShow(true) }
  const abrirEditar = u => {
    setEditando(u)
    setForm({ nome:u.nome, username:u.username||'', email:u.email, password:'', confirmar_senha:'', telefone:u.telefone||'', cpf:u.cpf||'', perfil:u.perfil })
    setShow(true)
  }

  const salvar = async e => {
    e.preventDefault()
    if (form.password && form.password!==form.confirmar_senha) { toast.error('Senhas não coincidem!'); return }
    try {
      const payload = {...form}
      if (!payload.password) { delete payload.password; delete payload.confirmar_senha }
      if (editando) { await api.put(`/auth/users/${editando.id}/`, payload); toast.success('Atualizado!') }
      else          { await api.post('/auth/users/', payload); toast.success('Criado!') }
      setShow(false); carregar()
    } catch(e){ toast.error(Object.values(e.response?.data?.detalhes||e.response?.data||{}).flat().join(' | ')||'Erro') }
  }

  const desativar = async u => {
    if (!confirm(`Desativar ${u.nome}?`)) return
    try { await api.delete(`/auth/users/${u.id}/`); toast.success('Desativado.'); carregar() }
    catch { toast.error('Erro') }
  }

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Usuários" />
        <section className="page">
          <div className="actions-row">
            <button className="btn btn-primary" onClick={abrirNovo}>+ Novo Usuário</button>
          </div>
          <div className="table card mt-12">
            {loading ? <p style={{padding:16}}>Carregando...</p> : (
              <table>
                <thead><tr><th>Nome</th><th>Usuário</th><th>E-mail</th><th>Perfil</th><th>Status</th><th>Ações</th></tr></thead>
                <tbody>
                  {users.length===0
                    ? <tr><td colSpan={6} style={{textAlign:'center',opacity:.5,padding:24}}>Nenhum usuário.</td></tr>
                    : users.map(u=>(
                      <tr key={u.id}>
                        <td><strong>{u.nome}</strong></td>
                        <td>{u.username||'—'}</td>
                        <td>{u.email}</td>
                        <td>{u.perfil_display}</td>
                        <td><span className={`badge ${u.is_active?'badge-done':'badge-danger'}`}>{u.is_active?'Ativo':'Inativo'}</span></td>
                        <td>
                          <div style={{display:'flex',gap:4}}>
                            <button className="btn btn-muted btn-sm" onClick={()=>abrirEditar(u)}>✏️</button>
                            <button className="btn btn-danger btn-sm" onClick={()=>desativar(u)}>Desativar</button>
                          </div>
                        </td>
                      </tr>
                    ))
                  }
                </tbody>
              </table>
            )}
          </div>

          {show && (
            <div className="modal-overlay">
              <div className="modal-box" style={{width:'min(560px,94vw)'}}>
                <div className="modal-header">
                  <span className="modal-title">{editando?'✏️ Editar':'+ Novo Usuário'}</span>
                  <button className="modal-close" onClick={()=>setShow(false)}>×</button>
                </div>
                <form onSubmit={salvar} autoComplete="off">
                  <div className="form-grid">
                    <div><label className="form-label">Nome completo *</label><input className="input" value={form.nome} required onChange={f('nome')}/></div>
                    <div><label className="form-label">Nome de usuário</label><input className="input" value={form.username} onChange={f('username')} autoComplete="off"/></div>
                    <div><label className="form-label">E-mail *</label><input className="input" type="email" value={form.email} required onChange={f('email')} autoComplete="off"/></div>
                    <div><label className="form-label">Telefone</label><input className="input" value={form.telefone} onChange={f('telefone')}/></div>
                    <div><label className="form-label">Perfil *</label>
                      <select className="input" value={form.perfil} onChange={f('perfil')}>
                        <option value="administrador">Administrador</option>
                        <option value="funcionario">Funcionário</option>
                      </select>
                    </div>
                    <div></div>
                    <div><label className="form-label">Senha {editando&&'(deixe em branco para manter)'}</label><input className="input" type="password" value={form.password} required={!editando} onChange={f('password')} autoComplete="new-password"/></div>
                    <div><label className="form-label">Confirmar senha</label><input className="input" type="password" value={form.confirmar_senha} required={!editando} onChange={f('confirmar_senha')} autoComplete="new-password"/></div>
                  </div>
                  <div className="actions-row mt-16" style={{justifyContent:'flex-end'}}>
                    <button type="button" className="btn btn-muted" onClick={()=>setShow(false)}>Cancelar</button>
                    <button type="submit" className="btn btn-primary">{editando?'Salvar':'Criar'}</button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
