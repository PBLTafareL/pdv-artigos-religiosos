import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

const STATUS_CLS = {
  aberto:'badge-open', aprovado:'badge-pending',
  recusado:'badge-danger', convertido:'badge-done', expirado:'badge-danger'
}

export default function Quotations() {
  const [orcamentos, setOrcamentos] = useState([])
  const [loading,    setLoading]    = useState(true)
  const [filtro,     setFiltro]     = useState('')
  const [detalhe,    setDetalhe]    = useState(null)
  const [showRecusar,setShowRecusar]= useState(null)
  const [motivo,     setMotivo]     = useState('')
  const [imprimindo, setImprimindo] = useState(null)

  const carregar = async () => {
    setLoading(true)
    try {
      const p = filtro ? `?status=${filtro}` : ''
      const { data } = await api.get(`/quotations/${p}`)
      setOrcamentos(data.resultados || [])
    } catch { toast.error('Erro ao carregar') }
    finally { setLoading(false) }
  }
  useEffect(() => { carregar() }, [filtro])

  const verDetalhe = async id => {
    try { const { data } = await api.get(`/quotations/${id}/`); setDetalhe(data) }
    catch { toast.error('Erro ao carregar detalhe') }
  }

  const imprimir = async (id, numero) => {
    setImprimindo(id)
    try {
      const resp = await api.get(`/quotations/${id}/pdf/`, { responseType: 'blob' })
      const url  = URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }))
      // Abre em nova aba e dispara impressão automaticamente
      const win  = window.open(url, '_blank')
      if (win) {
        win.onload = () => {
          setTimeout(() => { win.print() }, 500)
        }
      } else {
        // Fallback: download direto
        const a = document.createElement('a')
        a.href = url; a.download = `orcamento_${numero}.pdf`; a.click()
      }
      toast.success(`Orçamento ${numero} pronto para impressão!`)
    } catch { toast.error('Erro ao gerar PDF') }
    finally { setImprimindo(null) }
  }

  const aprovar = async id => {
    try {
      await api.post(`/quotations/${id}/aprovar/`, {})
      toast.success('Aprovado!'); carregar(); setDetalhe(null)
    } catch (e) { toast.error(e.response?.data?.mensagem || 'Erro') }
  }

  const recusar = async id => {
    if (!motivo.trim()) { toast.error('Informe o motivo'); return }
    try {
      await api.post(`/quotations/${id}/recusar/`, { motivo })
      toast.success('Recusado.'); setShowRecusar(null); setMotivo(''); carregar(); setDetalhe(null)
    } catch (e) { toast.error(e.response?.data?.mensagem || 'Erro') }
  }

  const converter = async id => {
    if (!confirm('Converter em venda? O caixa deve estar aberto.')) return
    try {
      const { data } = await api.post(`/quotations/${id}/converter/`, {})
      toast.success(data.mensagem); carregar(); setDetalhe(null)
    } catch (e) { toast.error(e.response?.data?.mensagem || 'Erro') }
  }

  const fmt = v => parseFloat(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  const FILTROS = [
    { v:'', l:'Todos' }, { v:'aberto', l:'Abertos' }, { v:'aprovado', l:'Aprovados' },
    { v:'recusado', l:'Recusados' }, { v:'convertido', l:'Convertidos' }, { v:'expirado', l:'Expirados' },
  ]

  return (
    <div className="app">
      <Sidebar />
      <main>
        <Navbar title="Orçamentos" />
        <section className="page">

          <div className="actions-row">
            {FILTROS.map(f => (
              <button key={f.v} className={`btn ${filtro === f.v ? 'btn-primary' : 'btn-muted'}`}
                onClick={() => setFiltro(f.v)}>{f.l}</button>
            ))}
          </div>

          <div className="table card mt-12">
            {loading ? <p style={{ padding:16 }}>Carregando...</p> : (
              <table>
                <thead>
                  <tr><th>Número</th><th>Cliente</th><th>Responsável</th><th>Total</th><th>Validade</th><th>Status</th><th>Ações</th></tr>
                </thead>
                <tbody>
                  {orcamentos.length === 0
                    ? <tr><td colSpan={7} style={{ textAlign:'center', opacity:.5, padding:24 }}>Nenhum orçamento.</td></tr>
                    : orcamentos.map(o => (
                      <tr key={o.id}>
                        <td><strong>{o.numero}</strong></td>
                        <td>{o.cliente_nome}</td>
                        <td>{o.responsavel_nome}</td>
                        <td><strong>{fmt(o.total)}</strong></td>
                        <td>
                          {o.validade}
                          {o.esta_expirado && <span style={{ color:'var(--danger)', fontSize:11, marginLeft:6 }}>⚠️ Expirado</span>}
                        </td>
                        <td><span className={`badge ${STATUS_CLS[o.status] || 'badge-pending'}`}>{o.status}</span></td>
                        <td>
                          <div style={{ display:'flex', gap:4, flexWrap:'wrap' }}>
                            <button className="btn btn-muted btn-sm" onClick={() => verDetalhe(o.id)}>👁️ Ver</button>
                            <button className="btn btn-muted btn-sm"
                              disabled={imprimindo === o.id}
                              onClick={() => imprimir(o.id, o.numero)}
                              title="Imprimir orçamento">
                              {imprimindo === o.id ? '⏳' : '🖨️ Imprimir'}
                            </button>
                            {o.status === 'aberto' && (
                              <button className="btn btn-accent btn-sm" onClick={() => aprovar(o.id)}>✅</button>
                            )}
                            {['aberto','aprovado'].includes(o.status) && (
                              <button className="btn btn-danger btn-sm" onClick={() => setShowRecusar(o.id)}>✕</button>
                            )}
                            {['aberto','aprovado'].includes(o.status) && !o.esta_expirado && (
                              <button className="btn btn-primary btn-sm" onClick={() => converter(o.id)}>→ Venda</button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  }
                </tbody>
              </table>
            )}
          </div>

          {/* Modal detalhe */}
          {detalhe && (
            <div className="modal-overlay">
              <div className="modal-box">
                <div className="modal-header">
                  <span className="modal-title">Orçamento {detalhe.numero}</span>
                  <button className="modal-close" onClick={() => setDetalhe(null)}>×</button>
                </div>

                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:16 }}>
                  <div style={{ background:'var(--muted)', borderRadius:10, padding:12 }}>
                    <p style={{ fontSize:11, opacity:.6, marginBottom:4 }}>CLIENTE</p>
                    <p style={{ fontWeight:700 }}>{detalhe.cliente_nome}</p>
                    <p style={{ fontSize:12, opacity:.7 }}>{detalhe.cliente_email}</p>
                    <p style={{ fontSize:12, opacity:.7 }}>{detalhe.cliente_telefone}</p>
                  </div>
                  <div style={{ background:'var(--muted)', borderRadius:10, padding:12 }}>
                    <p style={{ fontSize:11, opacity:.6, marginBottom:4 }}>DETALHES</p>
                    <p><strong>Status:</strong> <span className={`badge ${STATUS_CLS[detalhe.status]}`}>{detalhe.status_display}</span></p>
                    <p style={{ fontSize:12 }}><strong>Validade:</strong> {detalhe.validade}</p>
                    <p style={{ fontSize:12 }}><strong>Responsável:</strong> {detalhe.responsavel_nome}</p>
                  </div>
                </div>

                {detalhe.observacao && (
                  <div style={{ background:'#fffbeb', border:'1px solid #fde68a', borderRadius:8, padding:10, marginBottom:12, fontSize:13 }}>
                    <strong>Obs:</strong> {detalhe.observacao}
                  </div>
                )}

                <div className="table" style={{ marginBottom:12 }}>
                  <table>
                    <thead><tr><th>Produto</th><th>Cód.</th><th>Un.</th><th>Qtd</th><th>Preço</th><th>Total</th></tr></thead>
                    <tbody>
                      {detalhe.itens?.map(i => (
                        <tr key={i.id}>
                          <td><strong>{i.produto_nome}</strong></td>
                          <td>{i.produto_codigo}</td>
                          <td>{i.unidade_medida}</td>
                          <td>{parseFloat(i.quantidade)}</td>
                          <td>{fmt(i.preco_unitario)}</td>
                          <td><strong>{fmt(i.total)}</strong></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div style={{ textAlign:'right', marginBottom:16 }}>
                  {parseFloat(detalhe.desconto_valor) > 0 && (
                    <p style={{ fontSize:13 }}>Subtotal: {fmt(detalhe.subtotal)}</p>
                  )}
                  {parseFloat(detalhe.desconto_valor) > 0 && (
                    <p style={{ fontSize:13, color:'var(--danger)' }}>Desconto: - {fmt(detalhe.desconto_valor)}</p>
                  )}
                  <p style={{ fontSize:18, fontWeight:800, color:'var(--accent)' }}>
                    Total: {fmt(detalhe.total)}
                  </p>
                </div>

                <div className="actions-row" style={{ justifyContent:'flex-end' }}>
                  <button className="btn btn-muted" onClick={() => imprimir(detalhe.id, detalhe.numero)}
                    disabled={imprimindo === detalhe.id}>
                    {imprimindo === detalhe.id ? '⏳ Gerando...' : '🖨️ Imprimir Orçamento'}
                  </button>
                  {detalhe.status === 'aberto' && (
                    <button className="btn btn-accent" onClick={() => aprovar(detalhe.id)}>✅ Aprovar</button>
                  )}
                  {['aberto','aprovado'].includes(detalhe.status) && (
                    <button className="btn btn-danger" onClick={() => setShowRecusar(detalhe.id)}>Recusar</button>
                  )}
                  {['aberto','aprovado'].includes(detalhe.status) && (
                    <button className="btn btn-primary" onClick={() => converter(detalhe.id)}>→ Converter em Venda</button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Modal recusar */}
          {showRecusar && (
            <div className="modal-overlay">
              <div style={{ background:'var(--card)', borderRadius:20, padding:28,
                width:'min(400px,94vw)', border:'1px solid var(--border)', boxShadow:'var(--shadow)' }}>
                <div className="modal-header">
                  <span className="modal-title">Recusar Orçamento</span>
                  <button className="modal-close" onClick={() => setShowRecusar(null)}>×</button>
                </div>
                <div className="form-row">
                  <label className="form-label">Motivo *</label>
                  <textarea className="input" rows={3} value={motivo}
                    onChange={e => setMotivo(e.target.value)} style={{ resize:'none' }}
                    placeholder="Informe o motivo da recusa..." />
                </div>
                <div className="actions-row mt-16" style={{ justifyContent:'flex-end' }}>
                  <button className="btn btn-muted" onClick={() => setShowRecusar(null)}>Cancelar</button>
                  <button className="btn btn-danger" onClick={() => recusar(showRecusar)}>Recusar</button>
                </div>
              </div>
            </div>
          )}

        </section>
      </main>
    </div>
  )
}
