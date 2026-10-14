import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

const VAZIO = { nome:'', username:'', email:'', password:'', confirmar_senha:'', telefone:'', cpf:'', data_nascimento:'', endereco:'', cidade:'', estado:'', cep:'' }

export default function Clients() {
  const [clientes, setClientes] = useState([])
  const [search, setSearch]     = useState('')
  const [loading, setLoading]   = useState(true)
  const [show, setShow]         = useState(false)
  const [editando, setEditando] = useState(null)
  const [form, setForm]         = useState(VAZIO)

  const f = k => e => setForm(p => ({...p,[k]:e.target.value}))

  const carregar = async () => {
    try { const {data}=await api.get(`/auth/clients/?search=${search}`); setClientes(data.resultados||[]) }
    catch { toast.error('Erro') } finally { setLoading(false) }
  }
  useEffect(() => { carregar() }, [search])

  const abrirNovo = () => { setEditando(null); setForm(VAZIO); setShow(true) }
  const abrirEditar = c => {
    setEditando(c)
    setForm({ nome:c.nome, username:c.username||'', email:c.email, password:'', confirmar_senha:'',
      telefone:c.telefone||'', cpf:c.cpf||'', data_nascimento:c.data_nascimento||'',
      endereco:c.endereco||'', cidade:c.cidade||'', estado:c.estado||'', cep:c.cep||'' })
    setShow(true)
  }

  const salvar = async e => {
    e.preventDefault()
    if (!editando && form.password !== form.confirmar_senha) { toast.error('Senhas não coincidem!'); return }
    try {
      const payload = {...form}
      if (editando) { delete payload.password; delete payload.confirmar_senha }
      if (editando) { await api.put(`/auth/clients/${editando.id}/`, payload); toast.success('Atualizado!') }
      else          { await api.post('/auth/clients/', payload); toast.success('Cliente criado!') }
      setShow(false); carregar()
    } catch(e){ toast.error(Object.values(e.response?.data?.detalhes||e.response?.data||{}).flat().join(' | ')||'Erro') }
  }

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Clientes" />
        <section className="page">
          <div className="actions-row">
            <button className="btn btn-primary" onClick={abrirNovo}>+ Novo Cliente</button>
            <input className="input" style={{maxWidth:300}} placeholder="Buscar por nome, e-mail ou CPF..." value={search} onChange={e=>setSearch(e.target.value)} />
          </div>

          <div className="table card mt-12">
            {loading ? <p style={{padding:16}}>Carregando...</p> : (
              <table>
                <thead><tr><th>Nome</th><th>Usuário</th><th>E-mail</th><th>Telefone</th><th>Cidade</th><th>Pontos</th><th>Compras</th><th>Vouchers</th><th>Ações</th></tr></thead>
                <tbody>
                  {clientes.length===0
                    ? <tr><td colSpan={9} style={{textAlign:'center',opacity:.5,padding:24}}>Nenhum cliente.</td></tr>
                    : clientes.map(c=>(
                      <tr key={c.id}>
                        <td><strong>{c.nome}</strong></td>
                        <td>{c.username||'—'}</td>
                        <td>{c.email}</td>
                        <td>{c.telefone||'—'}</td>
                        <td>{c.cidade||'—'}</td>
                        <td>🏆 <strong>{c.saldo_pontos}</strong></td>
                        <td>🛒 {c.total_compras}</td>
                        <td>{c.vouchers_disponiveis>0?<span style={{color:'var(--primary)',fontWeight:700}}>🎟️ {c.vouchers_disponiveis}</span>:'—'}</td>
                        <td><button className="btn btn-muted btn-sm" onClick={()=>abrirEditar(c)}>✏️ Editar</button></td>
                      </tr>
                    ))
                  }
                </tbody>
              </table>
            )}
          </div>

          {show && (
            <div className="modal-overlay">
              <div className="modal-box">
                <div className="modal-header">
                  <span className="modal-title">{editando?'✏️ Editar Cliente':'+ Novo Cliente'}</span>
                  <button className="modal-close" onClick={()=>setShow(false)}>×</button>
                </div>
                <form onSubmit={salvar} autoComplete="off">
                  <p style={{fontSize:13,fontWeight:700,opacity:.6,marginBottom:10}}>Acesso</p>
                  <div className="form-grid">
                    <div><label className="form-label">Nome de usuário</label><input className="input" value={form.username} onChange={f('username')} autoComplete="off"/></div>
                    <div><label className="form-label">E-mail *</label><input className="input" type="email" value={form.email} required onChange={f('email')} autoComplete="off"/></div>
                    {!editando&&<>
                      <div><label className="form-label">Senha *</label><input className="input" type="password" value={form.password} required onChange={f('password')} autoComplete="new-password"/></div>
                      <div><label className="form-label">Confirmar senha *</label><input className="input" type="password" value={form.confirmar_senha} required onChange={f('confirmar_senha')} autoComplete="new-password"/></div>
                    </>}
                  </div>
                  <p style={{fontSize:13,fontWeight:700,opacity:.6,margin:'16px 0 10px'}}>Dados pessoais</p>
                  <div className="form-grid">
                    <div><label className="form-label">Nome completo *</label><input className="input" value={form.nome} required onChange={f('nome')}/></div>
                    <div><label className="form-label">CPF</label><input className="input" value={form.cpf} onChange={f('cpf')}/></div>
                    <div><label className="form-label">Telefone</label><input className="input" value={form.telefone} onChange={f('telefone')}/></div>
                    <div><label className="form-label">Nascimento</label><input className="input" type="date" value={form.data_nascimento} onChange={f('data_nascimento')}/></div>
                  </div>
                  <p style={{fontSize:13,fontWeight:700,opacity:.6,margin:'16px 0 10px'}}>Endereço</p>
                  <div className="form-grid">
                    <div style={{gridColumn:'1/-1'}}><label className="form-label">Endereço</label><input className="input" value={form.endereco} onChange={f('endereco')}/></div>
                    <div><label className="form-label">Cidade</label><input className="input" value={form.cidade} onChange={f('cidade')}/></div>
                    <div><label className="form-label">Estado</label><input className="input" value={form.estado} onChange={f('estado')}/></div>
                    <div><label className="form-label">CEP</label><input className="input" value={form.cep} onChange={f('cep')}/></div>
                  </div>
                  <div className="actions-row mt-16" style={{justifyContent:'flex-end'}}>
                    <button type="button" className="btn btn-muted" onClick={()=>setShow(false)}>Cancelar</button>
                    <button type="submit" className="btn btn-primary">{editando?'Salvar':'Cadastrar'}</button>
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
