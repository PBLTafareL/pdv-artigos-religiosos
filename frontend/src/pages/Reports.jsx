import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

const hoje = new Date().toISOString().slice(0,10)

export default function Reports() {
  const [aba, setAba] = useState('vendas')
  const [di, setDi]   = useState(hoje)
  const [df, setDf]   = useState(hoje)
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(false)

  const buscar = async () => {
    setLoading(true); setDados(null)
    try {
      let url = ''
      if (aba==='vendas')    url = `/reports/vendas/?data_inicio=${di}&data_fim=${df}`
      if (aba==='produtos')  url = `/reports/produtos/?data_inicio=${di}&data_fim=${df}`
      if (aba==='estoque')   url = `/reports/estoque/`
      const {data} = await api.get(url)
      setDados(data)
    } catch { toast.error('Erro ao gerar relatório') } finally { setLoading(false) }
  }

  const baixarPDF = async () => {
    try {
      let url = ''
      if (aba==='vendas')  url = `/reports/vendas/?data_inicio=${di}&data_fim=${df}&formato=pdf`
      if (aba==='estoque') url = `/reports/estoque/?formato=pdf`
      const resp = await api.get(url, { responseType:'blob' })
      const blobUrl = URL.createObjectURL(new Blob([resp.data],{type:'application/pdf'}))
      const a = document.createElement('a'); a.href=blobUrl; a.download=`relatorio_${aba}.pdf`; a.click()
    } catch { toast.error('Erro ao gerar PDF') }
  }

  const fmt = v => parseFloat(v||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Relatórios" />
        <section className="page">
          <div className="tabs">
            {[['vendas','📊 Vendas'],['produtos','📦 Produtos Vendidos'],['estoque','🗃️ Estoque']].map(([v,l])=>(
              <button key={v} className={`btn ${aba===v?'btn-primary':'btn-muted'}`} onClick={()=>{setAba(v);setDados(null)}}>{l}</button>
            ))}
          </div>

          <div className="card mt-12">
            <div style={{display:'flex',gap:12,alignItems:'flex-end',flexWrap:'wrap'}}>
              {aba!=='estoque' && <>
                <div><label className="form-label">Data Inicial</label><input type="date" className="input" style={{width:160}} value={di} onChange={e=>setDi(e.target.value)}/></div>
                <div><label className="form-label">Data Final</label><input type="date" className="input" style={{width:160}} value={df} onChange={e=>setDf(e.target.value)}/></div>
              </>}
              <button className="btn btn-primary" onClick={buscar} disabled={loading}>{loading?'Gerando...':'Gerar Relatório'}</button>
              {dados && <button className="btn btn-muted" onClick={baixarPDF}>📄 Baixar PDF</button>}
            </div>
          </div>

          {dados && (
            <div className="table card mt-12">
              {aba==='vendas' && (
                <>
                  <p style={{padding:'0 0 12px',fontWeight:700}}>Total: {fmt(dados.reduce((s,v)=>s+v.total,0))} em {dados.length} venda(s)</p>
                  <table>
                    <thead><tr><th>#</th><th>Data</th><th>Operador</th><th>Cliente</th><th>Itens</th><th>Total</th><th>Pontos</th></tr></thead>
                    <tbody>{dados.map(v=>(
                      <tr key={v.id}><td>{v.id}</td><td>{new Date(v.criado_em).toLocaleString('pt-BR')}</td>
                      <td>{v.operador_nome}</td><td>{v.cliente_nome||'—'}</td><td>{v.total_itens}</td>
                      <td><strong>{fmt(v.total)}</strong></td><td>{v.pontos_gerados}</td></tr>
                    ))}</tbody>
                  </table>
                </>
              )}
              {aba==='produtos' && (
                <table>
                  <thead><tr><th>Código</th><th>Produto</th><th>Qtd Vendida</th><th>Receita</th></tr></thead>
                  <tbody>{dados.map((d,i)=>(
                    <tr key={i}><td>{d.produto__codigo}</td><td><strong>{d.produto__nome}</strong></td>
                    <td>{parseFloat(d.total_qty).toFixed(3)}</td><td>{fmt(d.total_valor)}</td></tr>
                  ))}</tbody>
                </table>
              )}
              {aba==='estoque' && (
                <table>
                  <thead><tr><th>Código</th><th>Nome</th><th>Categoria</th><th>Estoque</th><th>Mín</th><th>Unid</th><th>Status</th><th>Preço</th></tr></thead>
                  <tbody>{dados.map(d=>(
                    <tr key={d.id}>
                      <td>{d.codigo}</td><td><strong>{d.nome}</strong></td><td>{d.categoria_nome||'—'}</td>
                      <td>{d.quantidade_estoque}</td><td>{d.estoque_minimo}</td><td>{d.unidade_medida}</td>
                      <td><span className={`badge badge-${d.status_estoque}`}>{d.status_display}</span></td>
                      <td>{fmt(d.preco_venda)}</td>
                    </tr>
                  ))}</tbody>
                </table>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
