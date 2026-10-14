import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

export default function Invoices() {
  const [notas, setNotas] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCancel, setShowCancel] = useState(null)
  const [motivo, setMotivo] = useState('')

  const carregar = async () => {
    setLoading(true)
    try { const {data}=await api.get('/invoices/'); setNotas(data.resultados||[]) }
    catch { toast.error('Erro') } finally { setLoading(false) }
  }
  useEffect(() => { carregar() }, [])

  const baixar = async id => {
    try {
      const resp = await api.get(`/invoices/${id}/download/`, { responseType:'blob' })
      const url  = URL.createObjectURL(new Blob([resp.data],{type:'application/pdf'}))
      const a    = document.createElement('a'); a.href=url; a.download=`nota_${id}.pdf`; a.click()
    } catch { toast.error('Erro ao baixar PDF') }
  }

  const cancelar = async id => {
    if (!motivo.trim()) { toast.error('Informe o motivo'); return }
    try { await api.post(`/invoices/${id}/cancelar/`,{motivo}); toast.success('Nota cancelada.'); setShowCancel(null); setMotivo(''); carregar() }
    catch(e){ toast.error(e.response?.data?.mensagem||'Erro') }
  }

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Notas Fiscais" />
        <section className="page">
          <div className="table card">
            {loading ? <p style={{padding:16}}>Carregando...</p> : (
              <table>
                <thead><tr><th>Número</th><th>Cliente</th><th>Total</th><th>Status</th><th>Emitida em</th><th>Ações</th></tr></thead>
                <tbody>
                  {notas.length===0
                    ? <tr><td colSpan={6} style={{textAlign:'center',opacity:.5,padding:24}}>Nenhuma nota emitida.</td></tr>
                    : notas.map(n=>(
                      <tr key={n.id}>
                        <td><strong>{n.numero}</strong></td>
                        <td>{n.cliente_nome||'—'}</td>
                        <td>R$ {parseFloat(n.total).toFixed(2)}</td>
                        <td><span className={`badge ${n.status==='emitida'?'badge-done':'badge-danger'}`}>{n.status_display}</span></td>
                        <td>{new Date(n.emitida_em).toLocaleString('pt-BR')}</td>
                        <td>
                          <div style={{display:'flex',gap:4}}>
                            <button className="btn btn-muted btn-sm" onClick={()=>baixar(n.id)}>📄 PDF</button>
                            {n.status==='emitida'&&<button className="btn btn-danger btn-sm" onClick={()=>setShowCancel(n.id)}>Cancelar</button>}
                          </div>
                        </td>
                      </tr>
                    ))
                  }
                </tbody>
              </table>
            )}
          </div>

          {showCancel && (
            <div className="modal-overlay">
              <div style={{background:'var(--card)',borderRadius:20,padding:28,width:'min(400px,94vw)',border:'1px solid var(--border)',boxShadow:'var(--shadow)'}}>
                <div className="modal-header"><span className="modal-title">Cancelar Nota</span><button className="modal-close" onClick={()=>setShowCancel(null)}>×</button></div>
                <div className="form-row"><label className="form-label">Motivo *</label>
                  <textarea className="input" rows={3} value={motivo} onChange={e=>setMotivo(e.target.value)} style={{resize:'none'}}/></div>
                <div className="actions-row mt-16" style={{justifyContent:'flex-end'}}>
                  <button className="btn btn-muted" onClick={()=>setShowCancel(null)}>Cancelar</button>
                  <button className="btn btn-danger" onClick={()=>cancelar(showCancel)}>Confirmar Cancelamento</button>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
