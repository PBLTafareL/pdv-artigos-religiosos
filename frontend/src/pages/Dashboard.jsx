import { useState, useEffect, useRef } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'

const INTERVALO_SEGUNDOS = 30

export default function Dashboard() {
  const [d,        setD]        = useState(null)
  const [loading,  setLoading]  = useState(true)
  const [erro,     setErro]     = useState(false)
  const [contador, setContador] = useState(INTERVALO_SEGUNDOS)
  const [ultima,   setUltima]   = useState(null)
  const intervalRef  = useRef(null)
  const countdownRef = useRef(null)

  const carregar = async (silencioso = false) => {
    if (!silencioso) setLoading(true)
    setErro(false)
    try {
      const { data } = await api.get('/dashboard/')
      setD(data)
      setUltima(new Date())
      setContador(INTERVALO_SEGUNDOS)
    } catch {
      setErro(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregar()

    // Auto-refresh a cada 30 segundos
    intervalRef.current = setInterval(() => carregar(true), INTERVALO_SEGUNDOS * 1000)

    // Countdown visual
    countdownRef.current = setInterval(() => {
      setContador(c => (c <= 1 ? INTERVALO_SEGUNDOS : c - 1))
    }, 1000)

    return () => {
      clearInterval(intervalRef.current)
      clearInterval(countdownRef.current)
    }
  }, [])

  const fmt = v => parseFloat(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
  const horaAtualiz = ultima ? ultima.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'

  const kpis = [
    {
      label: 'Vendas Hoje',
      value: fmt(d?.resumo_dia?.total_vendas_dia),
      icone: '💰',
      cor:   'var(--accent)',
    },
    {
      label: 'Qtd Vendas',
      value: d?.resumo_dia?.quantidade_vendas ?? 0,
      icone: '🛒',
      cor:   'var(--primary)',
    },
    {
      label: 'Ticket Médio',
      value: fmt(d?.resumo_dia?.ticket_medio),
      icone: '📊',
      cor:   '#6366f1',
    },
    {
      label: 'Orçamentos Abertos',
      value: d?.orcamentos_pendentes ?? 0,
      icone: '📋',
      cor:   '#f97316',
    },
  ]

  return (
    <div className="app">
      <Sidebar />
      <main>
        <Navbar title="Dashboard" />
        <section className="page">

          {/* Barra de status */}
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center',
            marginBottom:14, padding:'8px 14px', background:'var(--card)',
            border:'1px solid var(--border)', borderRadius:12, fontSize:13 }}>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{ width:8, height:8, borderRadius:'50%',
                background: erro ? 'var(--danger)' : 'var(--accent)',
                display:'inline-block', animation: loading ? 'pulse 1s infinite' : 'none' }} />
              <span style={{ opacity:.7 }}>
                {loading ? 'Atualizando...' : erro ? 'Erro ao carregar' : `Atualizado às ${horaAtualiz}`}
              </span>
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:12 }}>
              <span style={{ opacity:.5, fontSize:12 }}>
                Próxima atualização em <strong>{contador}s</strong>
              </span>
              <button
                onClick={() => carregar()}
                disabled={loading}
                style={{ background:'var(--muted)', border:'1px solid var(--border)',
                  borderRadius:8, padding:'4px 12px', cursor:'pointer', fontSize:12,
                  fontFamily:'inherit', fontWeight:700, opacity: loading ? .5 : 1 }}>
                {loading ? '⏳' : '🔄 Atualizar'}
              </button>
            </div>
          </div>

          {/* KPIs em tempo real */}
          <div className="kpis">
            {kpis.map((k, i) => (
              <div key={i} className="card kpi" style={{ position:'relative', overflow:'hidden' }}>
                <div style={{ position:'absolute', top:14, right:14, fontSize:24, opacity:.15 }}>
                  {k.icone}
                </div>
                <div className="label">{k.label}</div>
                <div className="value" style={{ color: k.cor, transition:'all .4s ease' }}>
                  {loading && !d ? (
                    <span style={{ opacity:.3, fontSize:18 }}>Carregando...</span>
                  ) : k.value}
                </div>
                {/* Barra indicadora colorida */}
                <div style={{ position:'absolute', bottom:0, left:0, right:0,
                  height:3, background:k.cor, opacity:.4, borderRadius:'0 0 16px 16px' }} />
              </div>
            ))}
          </div>

          {/* Gráfico */}
          {d?.vendas_por_dia?.length > 0 && (
            <div className="card mt-12">
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
                <div className="section-title" style={{ marginBottom:0 }}>Vendas por Dia (últimos 7 dias)</div>
                <span style={{ fontSize:12, opacity:.5 }}>
                  Total: {fmt(d.vendas_por_dia.reduce((s, v) => s + parseFloat(v.soma || 0), 0))}
                </span>
              </div>
              <div className="chart-bars">
                {(() => {
                  const vals = d.vendas_por_dia.map(v => parseFloat(v.soma || v.total || 0))
                  const max  = Math.max(...vals, 1)
                  return d.vendas_por_dia.slice(-7).map((v, i) => {
                    const val = parseFloat(v.soma || v.total || 0)
                    const pct = Math.max(10, (val / max) * 180)
                    return (
                      <div key={i} style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
                        <span style={{ fontSize:10, opacity:.6, fontWeight:700 }}>
                          {fmt(val).replace('R$','').trim()}
                        </span>
                        <div className="bar" style={{ height: pct + 'px', width:'100%', flexDirection:'column',
                          justifyContent:'flex-end', paddingBottom:6, position:'relative' }}
                          title={`${String(v.dia)} — ${v.quantidade} venda(s) — ${fmt(val)}`}>
                          <span style={{ fontSize:11, fontWeight:800 }}>
                            {String(v.dia).slice(8, 10)}/{String(v.dia).slice(5, 7)}
                          </span>
                        </div>
                        <span style={{ fontSize:10, opacity:.5 }}>{v.quantidade}v</span>
                      </div>
                    )
                  })
                })()}
              </div>
            </div>
          )}

          {/* Alertas */}
          {d?.alertas_estoque?.total > 0 && (
            <div className="card mt-12">
              <div className="section-title">⚠️ Alertas de Estoque ({d.alertas_estoque.total})</div>
              {d.alertas_estoque.alertas.map(a => (
                <div key={a.id} className="alerta-item">
                  <div>
                    <strong>{a.produto_nome}</strong>
                    <br /><small style={{ opacity:.6 }}>{a.produto_codigo}</small>
                  </div>
                  <div style={{ textAlign:'right' }}>
                    <span className={`badge badge-${a.status}`}>{a.status_display}</span>
                    <p style={{ fontSize:12, marginTop:2 }}>
                      Atual: {parseFloat(a.quantidade_atual)} / Mín: {parseFloat(a.estoque_minimo)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Produtos mais vendidos */}
          {d?.produtos_mais_vendidos?.length > 0 && (
            <div className="card table mt-12">
              <div className="section-title" style={{ padding:'0 0 12px' }}>🏆 Produtos Mais Vendidos</div>
              <table>
                <thead><tr><th>#</th><th>Produto</th><th>Código</th><th>Qtd Vendida</th><th>Receita</th></tr></thead>
                <tbody>
                  {d.produtos_mais_vendidos.map((p, i) => (
                    <tr key={i}>
                      <td><strong style={{ fontSize:15 }}>
                        {['🥇','🥈','🥉'][i] || `${i+1}º`}
                      </strong></td>
                      <td><strong>{p.produto__nome}</strong></td>
                      <td style={{ opacity:.6 }}>{p.produto__codigo}</td>
                      <td>{parseFloat(p.total_vendido).toFixed(3)}</td>
                      <td><strong style={{ color:'var(--accent)' }}>{fmt(p.total_receita)}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Estado vazio */}
          {d && !d.produtos_mais_vendidos?.length && !d.alertas_estoque?.total && (
            <div className="card mt-12" style={{ textAlign:'center', padding:40, opacity:.5 }}>
              <p style={{ fontSize:32, marginBottom:8 }}>📊</p>
              <p>Nenhuma venda hoje. Faça a primeira venda para ver os dados aqui!</p>
            </div>
          )}

        </section>
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}
