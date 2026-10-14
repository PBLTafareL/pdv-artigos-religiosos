import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

export default function Loyalty() {
  const [ranking, setRanking] = useState([])
  const [extrato, setExtrato] = useState(null)
  const [loadR, setLoadR]     = useState(true)
  const [search, setSearch]   = useState('')
  const [clientes, setClientes] = useState([])

  useEffect(() => {
    api.get('/loyalty/ranking/').then(r=>setRanking(r.data)).catch(()=>toast.error('Erro')).finally(()=>setLoadR(false))
  },[])

  const buscarClientes = async e => {
    const v = e.target.value; setSearch(v)
    if (v.length<2) { setClientes([]); return }
    try { const {data}=await api.get(`/auth/clients/?search=${v}`); setClientes(data.resultados||[]) } catch {}
  }

  const verExtrato = async c => {
    setClientes([]); setSearch(c.nome)
    try { const {data}=await api.get(`/loyalty/extrato/${c.id}/`); setExtrato(data) }
    catch { toast.error('Erro ao carregar extrato') }
  }

  const fmt = v => parseFloat(v||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Fidelidade" />
        <section className="page">

          {/* Busca extrato */}
          <div className="card" style={{marginBottom:16,position:'relative'}}>
            <div className="section-title">🔍 Consultar Extrato de Cliente</div>
            <input className="input" style={{maxWidth:400}} placeholder="Buscar cliente por nome ou CPF..." value={search} onChange={buscarClientes} />
            {clientes.length>0 && (
              <div style={{position:'absolute',left:20,right:20,background:'var(--card)',border:'1px solid var(--border)',borderRadius:10,boxShadow:'var(--shadow)',zIndex:10,maxHeight:200,overflowY:'auto',marginTop:4}}>
                {clientes.map(c=>(
                  <button key={c.id} onClick={()=>verExtrato(c)} style={{width:'100%',textAlign:'left',padding:'10px 14px',background:'none',border:'none',borderBottom:'1px solid var(--border)',cursor:'pointer',fontFamily:'inherit'}}>
                    <p style={{fontWeight:700,fontSize:13}}>{c.nome}</p>
                    <p style={{fontSize:12,opacity:.6}}>🏆 {c.saldo_pontos} pts · 🛒 {c.total_compras} compras · 🎟️ {c.vouchers_disponiveis} vouchers</p>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Extrato */}
          {extrato && (
            <div className="card mt-12" style={{marginBottom:16}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',flexWrap:'wrap',gap:12}}>
                <div>
                  <div className="section-title">📋 Extrato — {extrato.cliente}</div>
                  <div style={{display:'flex',gap:20,flexWrap:'wrap'}}>
                    <div><p style={{fontSize:12,opacity:.6}}>Saldo atual</p><p style={{fontWeight:800,fontSize:18,color:'var(--accent)'}}>🏆 {extrato.saldo_pontos} pts</p></div>
                    <div><p style={{fontSize:12,opacity:.6}}>Total compras</p><p style={{fontWeight:800,fontSize:18}}>🛒 {extrato.total_compras}</p></div>
                    <div><p style={{fontSize:12,opacity:.6}}>Vouchers</p><p style={{fontWeight:800,fontSize:18,color:'var(--primary)'}}>🎟️ {extrato.vouchers_disponiveis}</p></div>
                    <div><p style={{fontSize:12,opacity:.6}}>Falta p/ próx. voucher</p><p style={{fontWeight:800,fontSize:18}}>🛒 {extrato.proxima_compra_voucher}</p></div>
                  </div>
                </div>
                <button className="btn btn-muted btn-sm" onClick={()=>{setExtrato(null);setSearch('')}}>×</button>
              </div>
              {extrato.extrato?.length>0 && (
                <div className="table mt-12">
                  <table>
                    <thead><tr><th>Tipo</th><th>Pontos</th><th>Saldo após</th><th>Descrição</th><th>Data</th></tr></thead>
                    <tbody>{extrato.extrato.map(e=>(
                      <tr key={e.id}>
                        <td><span className={`badge ${e.tipo==='credito'?'badge-done':'badge-danger'}`}>{e.tipo_display}</span></td>
                        <td style={{color:e.tipo==='credito'?'var(--accent)':'var(--danger)',fontWeight:700}}>{e.tipo==='credito'?'+':'-'}{e.pontos}</td>
                        <td>{e.saldo_apos}</td>
                        <td>{e.descricao}</td>
                        <td>{new Date(e.criado_em).toLocaleString('pt-BR')}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Ranking */}
          <div className="card table mt-12">
            <div className="section-title" style={{padding:'0 0 12px'}}>🏆 Top 10 Clientes Mais Fidelizados</div>
            {loadR ? <p>Carregando...</p> : (
              <table>
                <thead><tr><th>#</th><th>Cliente</th><th>Pontos</th><th>Compras</th><th>Vouchers</th><th>Falta p/ próx.</th></tr></thead>
                <tbody>{ranking.map((c,i)=>(
                  <tr key={c.id}>
                    <td><strong style={{fontSize:16}}>{'🥇🥈🥉'[i]||`${i+1}º`}</strong></td>
                    <td><strong>{c.nome}</strong><br/><small style={{opacity:.6}}>{c.email}</small></td>
                    <td>🏆 <strong>{c.saldo_pontos}</strong></td>
                    <td>🛒 {c.total_compras}</td>
                    <td>{c.vouchers_disponiveis>0?<span style={{color:'var(--primary)',fontWeight:700}}>🎟️ {c.vouchers_disponiveis}</span>:'—'}</td>
                    <td>🛒 {c.proxima_compra_voucher}</td>
                  </tr>
                ))}</tbody>
              </table>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}
