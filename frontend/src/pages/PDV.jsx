import { useState, useEffect, useRef } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import Pagamento from '../components/pdv/Pagamento'
import OrcamentoPDV from '../components/pdv/OrcamentoPDV'
import api from '../api/api'
import toast from 'react-hot-toast'

const INTEIRAS = ['un','cx','pct']

export default function PDV() {
  const [sessao,  setSessao]  = useState(null)
  const [venda,   setVenda]   = useState(null)
  const [fundo,   setFundo]   = useState('')
  const [abrindo, setAbrindo] = useState(false)
  const [termo,   setTermo]   = useState('')
  const [res,     setRes]     = useState([])
  const [qtdMap,  setQtdMap]  = useState({})
  const [cliente, setCliente] = useState(null)
  const [buscaCli,setBuscaCli]= useState('')
  const [clientes,setClientes]= useState([])
  const [showPag, setShowPag] = useState(false)
  const [showOrc, setShowOrc] = useState(false)
  const [showVch, setShowVch] = useState(false)
  const bcRef = useRef(''); const bcTimer = useRef(null); const loadingRef = useRef(false)

  useEffect(() => {
    api.get('/pdv/caixa/atual/').then(r=>setSessao(r.data)).catch(()=>{})
  },[])

  // Leitor código de barras
  useEffect(() => {
    const onKey = e => {
      if (['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) return
      if (e.key==='Enter' && bcRef.current.length>2) {
        buscarCodigo(bcRef.current); bcRef.current=''; return
      }
      if (e.key.length===1) {
        bcRef.current += e.key
        clearTimeout(bcTimer.current)
        bcTimer.current = setTimeout(()=>{ bcRef.current='' },150)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  },[venda])

  const buscarCodigo = async codigo => {
    try {
      const { data } = await api.get(`/products/pdv-search/?q=${codigo}`)
      const r = data.resultados||[]
      if (r.length===1) { addProduto(r[0]); toast.success(`${r[0].nome} adicionado!`) }
      else if (r.length>1) { setRes(r); setTermo(codigo) }
      else toast.error('Produto não encontrado.')
    } catch {}
  }

  const buscarProdutos = async e => {
    const v = e.target.value; setTermo(v)
    if (v.length<2) { setRes([]); return }
    try { const {data}=await api.get(`/products/pdv-search/?q=${v}`); setRes(data.resultados||[]) } catch { setRes([]) }
  }

  const buscarClientes = async e => {
    const v = e.target.value; setBuscaCli(v)
    if (v.length<2) { setClientes([]); return }
    try { const {data}=await api.get(`/auth/clients/?search=${v}`); setClientes(data.resultados||[]) } catch { setClientes([]) }
  }

  const abrirCaixa = async () => {
    setAbrindo(true)
    try {
      const {data}=await api.post('/pdv/caixa/abrir/',{fundo_caixa:parseFloat(fundo)||0})
      setSessao(data.sessao); toast.success('Caixa aberto!')
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro') } finally { setAbrindo(false) }
  }

  const fecharCaixa = async () => {
    if(!confirm('Fechar o caixa?')) return
    try { await api.post(`/pdv/caixa/${sessao.id}/fechar/`,{}); setSessao(null); setVenda(null); toast.success('Caixa fechado!') }
    catch { toast.error('Erro ao fechar') }
  }

  const novaVenda = async () => {
    try {
      const {data}=await api.post('/pdv/vendas/iniciar/',{tipo:'venda'})
      setVenda(data.venda); setCliente(null); setBuscaCli(''); setClientes([])
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro') }
  }

  const addProduto = async produto => {
    if (!venda) { toast.error('Inicie uma venda primeiro'); return }
    const inteiro = INTEIRAS.includes(produto.unidade_medida||'un')
    const qtdRaw  = parseFloat(qtdMap[produto.id]??1)
    const qtd     = inteiro ? Math.max(1, Math.floor(qtdRaw)) : qtdRaw
    if (qtd<=0) { toast.error('Quantidade inválida'); return }
    try {
      const {data}=await api.post(`/pdv/vendas/${venda.id}/itens/`,{produto_id:produto.id,quantidade:qtd})
      setVenda(data.venda); setRes([]); setTermo(''); setQtdMap(p=>({...p,[produto.id]:1}))
    } catch(e){ toast.error(e.response?.data?.mensagem||'Estoque insuficiente') }
  }

  const remItem = async itemId => {
    try { const {data}=await api.delete(`/pdv/vendas/${venda.id}/itens/${itemId}/`); setVenda(data.venda) }
    catch { toast.error('Erro') }
  }

  const vincularCliente = async c => {
    try {
      const {data}=await api.post(`/pdv/vendas/${venda.id}/cliente/`,{cliente_id:c.id})
      setCliente(data.cliente); setClientes([]); setBuscaCli(c.nome); setVenda(data.venda)
      toast.success(`${c.nome} vinculado!`)
      if (data.cliente.vouchers_disponiveis>0) setShowVch(true)
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro') }
  }

  const usarVoucher = async usar => {
    setShowVch(false)
    if (!usar) return
    try {
      const {data}=await api.post(`/pdv/vendas/${venda.id}/voucher/`,{})
      setVenda(data.venda); toast.success('🎉 Voucher de R$50 aplicado!')
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro') }
  }

  const pagar = async dados => {
    try {
      await api.post(`/pdv/vendas/${venda.id}/pagamento/`,dados)
      const {data}=await api.post(`/pdv/vendas/${venda.id}/finalizar/`,{})
      let msg = `✅ Finalizado! Pontos: ${data.pontos_gerados}`
      if (data.ganhou_voucher) msg += ' | 🎉 Cliente ganhou voucher de R$50!'
      toast.success(msg,{duration:5000})
      try { await api.post(`/invoices/emitir/${venda.id}/`,{}) } catch {}
      setVenda(null); setShowPag(false); setCliente(null); setBuscaCli('')
      api.get('/pdv/caixa/atual/').then(r=>setSessao(r.data)).catch(()=>{})
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro ao finalizar') }
  }

  const salvarOrc = async ({validade,observacao}) => {
    if (!cliente) { toast.error('Vincule um cliente para salvar orçamento'); return }
    try {
      const {data}=await api.post(`/pdv/vendas/${venda.id}/orcamento/`,{validade,observacao})
      toast.success(data.mensagem); setVenda(null); setShowOrc(false)
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro') }
  }

  const cancelar = async () => {
    if (!confirm('Cancelar venda?')) return
    try { await api.post(`/pdv/vendas/${venda.id}/cancelar/`,{}); setVenda(null); setCliente(null); toast.success('Cancelada') }
    catch { toast.error('Erro') }
  }

  const total = parseFloat(venda?.total||0)
  const itens = venda?.itens||[]

  if (!sessao) return (
    <div className="app"><Sidebar />
      <main><Navbar title="Venda (Caixa)" />
        <section className="page">
          <div style={{maxWidth:400,margin:'60px auto'}}>
            <div className="card" style={{textAlign:'center'}}>
              <div style={{fontSize:48,marginBottom:12}}>🛒</div>
              <div className="section-title">Abrir Caixa</div>
              <div className="form-row"><label className="form-label">Fundo de caixa (R$)</label>
                <input type="number" className="input" value={fundo} onChange={e=>setFundo(e.target.value)} placeholder="0,00" min="0" step=".01" /></div>
              <button className="btn btn-accent" style={{width:'100%',justifyContent:'center'}} onClick={abrirCaixa} disabled={abrindo}>
                {abrindo?'Abrindo...':'✅ Abrir Caixa'}</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  )

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Venda (Caixa)" />
        <section className="page">
          {/* Barra caixa */}
          <div className="card" style={{marginBottom:16,display:'flex',alignItems:'center',justifyContent:'space-between',flexWrap:'wrap',gap:8}}>
            <div style={{display:'flex',gap:16,alignItems:'center',flexWrap:'wrap'}}>
              <span style={{fontWeight:800}}>Caixa #{sessao.id}</span>
              <span style={{fontSize:13}}>Vendas: <strong style={{color:'var(--accent)'}}>R$ {parseFloat(sessao.total_vendas||0).toFixed(2)}</strong></span>
              <span style={{fontSize:13}}>Saldo: <strong>R$ {parseFloat(sessao.saldo_calculado||0).toFixed(2)}</strong></span>
              <span style={{fontSize:11,opacity:.5,background:'var(--muted)',padding:'2px 8px',borderRadius:6}}>🔍 Leitor barras ativo</span>
            </div>
            <div className="actions-row" style={{marginBottom:0}}>
              {!venda && <button className="btn btn-accent" onClick={novaVenda}>+ Nova Venda</button>}
              <button className="btn btn-danger" onClick={fecharCaixa}>Fechar Caixa</button>
            </div>
          </div>

          <div className="grid-sale">
            <div>
              {/* Busca */}
              <div className="card" style={{marginBottom:16}}>
                <div className="section-title">Adicionar Itens</div>
                <div style={{position:'relative'}}>
                  <div style={{display:'flex',alignItems:'center',background:'var(--muted)',border:'1.5px solid var(--border)',borderRadius:10,padding:'0 12px'}}>
                    <span style={{opacity:.5,marginRight:8}}>🔍</span>
                    <input style={{flex:1,background:'none',border:'none',outline:'none',padding:'11px 0',fontSize:14,color:'var(--text)',fontFamily:'inherit'}}
                      placeholder="Nome, código ou passe pelo leitor de barras..."
                      value={termo} onChange={buscarProdutos} />
                  </div>
                  {res.length>0 && (
                    <div style={{position:'absolute',top:'100%',left:0,right:0,background:'var(--card)',border:'1px solid var(--border)',borderRadius:12,boxShadow:'var(--shadow)',zIndex:500,maxHeight:360,overflowY:'auto',marginTop:4}}>
                      {res.map(p => {
                        const inteiro = INTEIRAS.includes(p.unidade_medida||'un')
                        return (
                          <div key={p.id} style={{borderBottom:'1px solid var(--border)',padding:'10px 14px'}}>
                            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:8}}>
                              <div style={{flex:1}}>
                                <p style={{fontWeight:700,fontSize:14}}>{p.nome}</p>
                                <p style={{fontSize:12,opacity:.6}}>{p.codigo} · Estoque: {parseFloat(p.quantidade_estoque)} {p.unidade_medida}</p>
                              </div>
                              <strong style={{color:'var(--accent)',whiteSpace:'nowrap'}}>R$ {parseFloat(p.preco_venda).toFixed(2)}</strong>
                              <div style={{display:'flex',alignItems:'center',gap:6}}>
                                <input type="number" style={{width:60,padding:'5px 8px',borderRadius:8,border:'1.5px solid var(--border)',fontSize:13,textAlign:'center',fontFamily:'inherit'}}
                                  value={qtdMap[p.id]??1} min={inteiro?1:0.001} step={inteiro?1:0.001}
                                  onChange={e=>setQtdMap(prev=>({...prev,[p.id]:e.target.value}))}
                                  onClick={e=>e.stopPropagation()} />
                                <span style={{fontSize:11,opacity:.6}}>{p.unidade_medida}</span>
                                <button className="btn btn-accent btn-sm" onClick={()=>addProduto(p)}>+ Add</button>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </div>

              {/* Carrinho */}
              {venda && (
                <div className="card table">
                  <table>
                    <thead><tr><th>Produto</th><th>Qtd</th><th>Un</th><th>Unit.</th><th>Total</th><th></th></tr></thead>
                    <tbody>
                      {itens.length===0
                        ? <tr><td colSpan={6} style={{textAlign:'center',opacity:.5,padding:24}}>Nenhum item no carrinho.</td></tr>
                        : itens.map(item=>(
                          <tr key={item.id}>
                            <td><strong>{item.produto_nome}</strong><br/><small style={{opacity:.6}}>{item.produto_codigo}</small></td>
                            <td>{item.e_inteiro ? parseInt(item.quantidade) : parseFloat(item.quantidade).toFixed(3)}</td>
                            <td>{item.unidade_medida}</td>
                            <td>R$ {parseFloat(item.preco_unitario).toFixed(2)}</td>
                            <td><strong>R$ {parseFloat(item.total).toFixed(2)}</strong></td>
                            <td><button onClick={()=>remItem(item.id)} style={{background:'none',border:'none',color:'var(--danger)',cursor:'pointer',fontWeight:700}}>✕</button></td>
                          </tr>
                        ))
                      }
                    </tbody>
                    {itens.length>0 && <tfoot><tr><td colSpan={4} style={{textAlign:'right'}}>Total</td><td colSpan={2}><strong>R$ {total.toFixed(2)}</strong></td></tr></tfoot>}
                  </table>
                </div>
              )}
            </div>

            {/* Painel direito */}
            <div>
              {venda ? (<>
                {/* Cliente */}
                <div className="card" style={{marginBottom:16,position:'relative'}}>
                  <div className="section-title">👤 Cliente</div>
                  {cliente ? (
                    <div style={{background:'var(--muted)',borderRadius:10,padding:'10px 14px'}}>
                      <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}>
                        <div>
                          <p style={{fontWeight:700}}>{cliente.nome}</p>
                          <p style={{fontSize:12,color:'var(--accent)'}}>🏆 {cliente.saldo_pontos} pontos</p>
                          <p style={{fontSize:12}}>🛒 {cliente.total_compras} compras · falta {cliente.proxima_compra_voucher} p/ voucher</p>
                          {cliente.vouchers_disponiveis>0 && <p style={{fontSize:12,color:'var(--primary)',fontWeight:700}}>🎟️ {cliente.vouchers_disponiveis} voucher(s) disponível(is)</p>}
                        </div>
                        <button onClick={()=>{setCliente(null);setBuscaCli('')}} style={{background:'none',border:'none',color:'var(--danger)',cursor:'pointer',fontSize:20}}>×</button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <input className="input" placeholder="Buscar cliente por nome ou CPF..." value={buscaCli} onChange={buscarClientes} autoComplete="off" />
                      {clientes.length>0 && (
                        <div style={{background:'var(--card)',border:'1px solid var(--border)',borderRadius:10,marginTop:4,maxHeight:180,overflowY:'auto',boxShadow:'var(--shadow)',position:'absolute',left:20,right:20,zIndex:100}}>
                          {clientes.map(c=>(
                            <button key={c.id} onClick={()=>vincularCliente(c)} style={{width:'100%',textAlign:'left',padding:'10px 14px',background:'none',border:'none',borderBottom:'1px solid var(--border)',cursor:'pointer',fontFamily:'inherit'}}>
                              <p style={{fontWeight:700,fontSize:13}}>{c.nome}</p>
                              <p style={{fontSize:12,opacity:.6}}>{c.cpf} · 🏆 {c.saldo_pontos} pts · 🛒 {c.total_compras} compras</p>
                            </button>
                          ))}
                        </div>
                      )}
                      <p style={{fontSize:11,opacity:.5,marginTop:4}}>Opcional — necessário para acumular pontos</p>
                    </div>
                  )}
                </div>

                {/* Resumo */}
                <div className="card summary" style={{marginBottom:16}}>
                  <div className="section-title">Resumo</div>
                  <div className="row"><span>Subtotal</span><strong>R$ {parseFloat(venda.subtotal||0).toFixed(2)}</strong></div>
                  {parseFloat(venda.desconto_valor||0)>0 && <div className="row"><span>Desconto</span><strong style={{color:'var(--danger)'}}>- R$ {parseFloat(venda.desconto_valor).toFixed(2)}</strong></div>}
                  <div className="total"><span>Total</span><strong>R$ {total.toFixed(2)}</strong></div>
                </div>

                {/* Ações */}
                <div className="card">
                  <div style={{display:'flex',flexDirection:'column',gap:8}}>
                    <button className="btn btn-accent" style={{justifyContent:'center'}} disabled={itens.length===0} onClick={()=>setShowPag(true)}>
                      💳 Finalizar — R$ {total.toFixed(2)}
                    </button>
                    <button className="btn btn-muted" style={{justifyContent:'center'}} onClick={()=>setShowOrc(true)}>💰 Salvar como Orçamento</button>
                    <button className="btn btn-danger" style={{justifyContent:'center'}} onClick={cancelar}>✕ Cancelar Venda</button>
                  </div>
                </div>
              </>) : (
                <div className="card" style={{textAlign:'center',padding:40,opacity:.5}}>
                  <p style={{fontSize:32}}>🛒</p><p>Clique em "Nova Venda" para começar</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </main>

      {/* Modal voucher */}
      {showVch && cliente && (
        <div className="modal-overlay">
          <div style={{background:'var(--card)',borderRadius:20,padding:28,width:'min(400px,94vw)',border:'1px solid var(--border)',boxShadow:'var(--shadow)',textAlign:'center'}}>
            <div style={{fontSize:48,marginBottom:8}}>🎟️</div>
            <h3 style={{fontWeight:800,fontSize:18,marginBottom:8}}>Voucher Disponível!</h3>
            <p style={{marginBottom:20,fontSize:14}}><strong>{cliente.nome}</strong> tem <strong>{cliente.vouchers_disponiveis} voucher(s)</strong> de R$50,00 por fidelidade.<br/><span style={{opacity:.7,fontSize:13}}>Deseja usar nesta compra?</span></p>
            <div style={{display:'flex',gap:8}}>
              <button className="btn btn-muted" style={{flex:1,justifyContent:'center'}} onClick={()=>usarVoucher(false)}>Guardar para próxima</button>
              <button className="btn btn-accent" style={{flex:1,justifyContent:'center'}} onClick={()=>usarVoucher(true)}>✅ Usar agora (- R$50)</button>
            </div>
          </div>
        </div>
      )}

      {showPag && <Pagamento total={total} clientePontos={cliente?.saldo_pontos||0} onPagar={pagar} onClose={()=>setShowPag(false)} />}
      {showOrc && <OrcamentoPDV onSalvar={salvarOrc} onClose={()=>setShowOrc(false)} />}
    </div>
  )
}
