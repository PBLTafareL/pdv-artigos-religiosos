import { useState, useEffect, useRef } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar  from '../components/Navbar'
import api     from '../api/api'
import toast   from 'react-hot-toast'

const VAZIO   = { codigo:'', codigo_barras:'', nome:'', descricao:'', preco_custo:'', preco_venda:'', quantidade_estoque:'', estoque_minimo:'0', unidade_medida:'un', categoria:'' }
const VAZIO_C = { nome:'', descricao:'' }
const INTEIRAS = ['un','cx','pct']

export default function Products() {
  const [aba,       setAba]       = useState('produtos')
  const [produtos,  setProdutos]  = useState([])
  const [categorias,setCategorias]= useState([])
  const [search,    setSearch]    = useState('')
  const [loading,   setLoading]   = useState(true)
  const [showForm,  setShowForm]  = useState(false)
  const [showCat,   setShowCat]   = useState(false)
  const [editando,  setEditando]  = useState(null)
  const [editCat,   setEditCat]   = useState(null)
  const [form,      setForm]      = useState(VAZIO)
  const [formCat,   setFormCat]   = useState(VAZIO_C)
  const [imagem,    setImagem]    = useState(null)
  const [preview,   setPreview]   = useState(null)
  const barcodeInput = useRef(null)

  const carregarCats = async () => {
    try { const {data}=await api.get('/products/categories/'); setCategorias(data.resultados||[]) } catch {}
  }
  const carregarProd = async () => {
    setLoading(true)
    try { const {data}=await api.get(`/products/?search=${search}`); setProdutos(data.resultados||[]) }
    catch { toast.error('Erro ao carregar') } finally { setLoading(false) }
  }
  useEffect(() => { carregarCats() }, [])
  useEffect(() => { carregarProd() }, [search])

  const f = k => e => setForm(p => ({...p,[k]:e.target.value}))
  const fc = k => e => setFormCat(p => ({...p,[k]:e.target.value}))

  const abrirNovo = () => { setEditando(null); setForm(VAZIO); setImagem(null); setPreview(null); setShowForm(true) }
  const abrirEditar = p => {
    setEditando(p)
    setForm({ codigo:p.codigo, codigo_barras:p.codigo_barras||'', nome:p.nome, descricao:p.descricao||'',
      preco_custo:p.preco_custo||'', preco_venda:p.preco_venda, quantidade_estoque:p.quantidade_estoque,
      estoque_minimo:p.estoque_minimo, unidade_medida:p.unidade_medida, categoria:p.categoria||'' })
    setPreview(p.imagem_url||null); setImagem(null); setShowForm(true)
  }

  const salvarProd = async e => {
    e.preventDefault()
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k,v]) => { if (v!=='') fd.append(k,v) })
      if (imagem) fd.append('imagem', imagem)
      const cfg = { headers:{'Content-Type':'multipart/form-data'} }
      if (editando) { await api.patch(`/products/${editando.id}/`, fd, cfg); toast.success('Produto atualizado!') }
      else          { await api.post('/products/', fd, cfg); toast.success('Produto criado!') }
      setShowForm(false); carregarProd()
    } catch(e){ toast.error(e.response?.data?.mensagem||Object.values(e.response?.data||{})[0]||'Erro') }
  }

  const excluirProd = async p => {
    if (!confirm(`Desativar "${p.nome}"?`)) return
    try { await api.delete(`/products/${p.id}/`); toast.success('Desativado.'); carregarProd() }
    catch { toast.error('Erro') }
  }

  const gerarBarcode = async p => {
    try {
      const {data} = await api.post(`/products/${p.id}/barcode/`,{})
      toast.success('Código de barras gerado!')
      carregarProd()
    } catch { toast.error('Erro ao gerar') }
  }

  const imprimirBarcode = url => {
    const w = window.open('','_blank')
    w.document.write(`<html><body style="text-align:center;padding:20px"><img src="${url}" style="max-width:300px"/><br/><button onclick="window.print()">Imprimir</button></body></html>`)
    w.document.close()
  }

  const salvarCat = async e => {
    e.preventDefault()
    try {
      if (editCat) { await api.put(`/products/categories/${editCat.id}/`, formCat); toast.success('Categoria atualizada!') }
      else         { await api.post('/products/categories/', formCat); toast.success('Categoria criada!') }
      setShowCat(false); carregarCats()
    } catch(e){ toast.error(e.response?.data?.mensagem||'Erro') }
  }

  const excluirCat = async c => {
    if (!confirm(`Excluir "${c.nome}"?`)) return
    try { await api.delete(`/products/categories/${c.id}/`); toast.success('Removida.'); carregarCats() }
    catch { toast.error('Erro') }
  }

  const statusCls = { normal:'badge-normal', baixo:'badge-baixo', zerado:'badge-zerado' }

  return (
    <div className="app"><Sidebar />
      <main><Navbar title="Produtos" />
        <section className="page">

          <div className="tabs">
            <button className={`btn ${aba==='produtos'?'btn-primary':'btn-muted'}`} onClick={()=>setAba('produtos')}>📦 Produtos</button>
            <button className={`btn ${aba==='categorias'?'btn-primary':'btn-muted'}`} onClick={()=>setAba('categorias')}>🏷️ Categorias</button>
          </div>

          {aba==='produtos' && <>
            <div className="actions-row">
              <button className="btn btn-primary" onClick={abrirNovo}>+ Novo Produto</button>
              <input className="input" style={{maxWidth:300}} placeholder="Buscar por nome ou código..." value={search} onChange={e=>setSearch(e.target.value)} />
            </div>
            <div className="table card mt-12">
              {loading ? <p style={{padding:16}}>Carregando...</p> : (
                <table>
                  <thead><tr><th>Foto</th><th>Nome/Código</th><th>Categoria</th><th>Preço</th><th>Estoque</th><th>Tipo</th><th>Status</th><th>Barcode</th><th>Ações</th></tr></thead>
                  <tbody>
                    {produtos.length===0
                      ? <tr><td colSpan={9} style={{textAlign:'center',opacity:.5,padding:24}}>Nenhum produto.</td></tr>
                      : produtos.map(p=>(
                        <tr key={p.id}>
                          <td>{p.imagem_url ? <img src={p.imagem_url} alt="" style={{width:36,height:36,borderRadius:8,objectFit:'cover'}}/> : <span style={{fontSize:20}}>📦</span>}</td>
                          <td><strong>{p.nome}</strong><br/><small style={{opacity:.6}}>{p.codigo}</small></td>
                          <td>{p.categoria_nome||'—'}</td>
                          <td>R$ {parseFloat(p.preco_venda).toFixed(2)}</td>
                          <td>{INTEIRAS.includes(p.unidade_medida)?parseInt(p.quantidade_estoque):parseFloat(p.quantidade_estoque).toFixed(3)} {p.unidade_medida}</td>
                          <td><span style={{fontSize:11,background:'var(--muted)',padding:'2px 6px',borderRadius:6}}>{INTEIRAS.includes(p.unidade_medida)?'Inteiro':'Decimal'}</span></td>
                          <td><span className={`badge ${statusCls[p.status_estoque]||'badge-pending'}`}>{p.status_display}</span></td>
                          <td>
                            {p.imagem_barcode_url
                              ? <button className="btn btn-muted btn-sm" onClick={()=>imprimirBarcode(p.imagem_barcode_url)}>🖨️</button>
                              : <button className="btn btn-muted btn-sm" onClick={()=>gerarBarcode(p)}>Gerar</button>}
                          </td>
                          <td>
                            <div style={{display:'flex',gap:4}}>
                              <button className="btn btn-muted btn-sm" onClick={()=>abrirEditar(p)}>✏️</button>
                              <button className="btn btn-danger btn-sm" onClick={()=>excluirProd(p)}>🗑️</button>
                            </div>
                          </td>
                        </tr>
                      ))
                    }
                  </tbody>
                </table>
              )}
            </div>
          </>}

          {aba==='categorias' && <>
            <div className="actions-row">
              <button className="btn btn-primary" onClick={()=>{setEditCat(null);setFormCat(VAZIO_C);setShowCat(true)}}>+ Nova Categoria</button>
            </div>
            <div className="table card mt-12">
              <table>
                <thead><tr><th>Nome</th><th>Descrição</th><th>Ações</th></tr></thead>
                <tbody>
                  {categorias.length===0
                    ? <tr><td colSpan={3} style={{textAlign:'center',opacity:.5,padding:24}}>Nenhuma categoria.</td></tr>
                    : categorias.map(c=>(
                      <tr key={c.id}>
                        <td><strong>{c.nome}</strong></td>
                        <td>{c.descricao||'—'}</td>
                        <td>
                          <div style={{display:'flex',gap:4}}>
                            <button className="btn btn-muted btn-sm" onClick={()=>{setEditCat(c);setFormCat({nome:c.nome,descricao:c.descricao||''});setShowCat(true)}}>✏️ Editar</button>
                            <button className="btn btn-danger btn-sm" onClick={()=>excluirCat(c)}>🗑️</button>
                          </div>
                        </td>
                      </tr>
                    ))
                  }
                </tbody>
              </table>
            </div>
          </>}

          {/* Modal Produto */}
          {showForm && (
            <div className="modal-overlay">
              <div className="modal-box">
                <div className="modal-header">
                  <span className="modal-title">{editando?'✏️ Editar Produto':'+ Novo Produto'}</span>
                  <button className="modal-close" onClick={()=>setShowForm(false)}>×</button>
                </div>
                <form onSubmit={salvarProd}>
                  {/* Foto */}
                  <div style={{textAlign:'center',marginBottom:16}}>
                    {preview ? <img src={preview} alt="" style={{width:80,height:80,borderRadius:12,objectFit:'cover',marginBottom:8}}/> : <div style={{width:80,height:80,borderRadius:12,background:'var(--muted)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:28,margin:'0 auto 8px'}}>📦</div>}
                    <label className="btn btn-muted btn-sm" style={{cursor:'pointer'}}>
                      📷 {preview?'Trocar foto':'Adicionar foto'}
                      <input type="file" accept="image/*" style={{display:'none'}} onChange={e=>{const f=e.target.files[0];if(f){setImagem(f);setPreview(URL.createObjectURL(f))}}}/>
                    </label>
                  </div>

                  <div className="form-grid">
                    <div><label className="form-label">Código *</label><input className="input" value={form.codigo} required disabled={!!editando} onChange={f('codigo')}/></div>
                    <div>
                      <label className="form-label">Código de Barras <span style={{fontSize:11,opacity:.6}}>(leitor ou manual)</span></label>
                      <input ref={barcodeInput} className="input" value={form.codigo_barras} onChange={f('codigo_barras')} placeholder="Passe o leitor ou digite..." />
                    </div>
                    <div style={{gridColumn:'1/-1'}}><label className="form-label">Nome *</label><input className="input" value={form.nome} required onChange={f('nome')}/></div>
                    <div><label className="form-label">Preço de Custo (R$)</label><input className="input" type="number" step=".01" value={form.preco_custo} onChange={f('preco_custo')}/></div>
                    <div><label className="form-label">Preço de Venda (R$) *</label><input className="input" type="number" step=".01" value={form.preco_venda} required onChange={f('preco_venda')}/></div>
                    <div>
                      <label className="form-label">Unidade *</label>
                      <select className="input" value={form.unidade_medida} onChange={f('unidade_medida')}>
                        <optgroup label="Inteiro (sem decimal)">
                          <option value="un">Unidade (un)</option><option value="cx">Caixa (cx)</option><option value="pct">Pacote (pct)</option>
                        </optgroup>
                        <optgroup label="Decimal (peso/medida)">
                          <option value="kg">Quilograma (kg)</option><option value="g">Grama (g)</option>
                          <option value="l">Litro (l)</option><option value="ml">Mililitro (ml)</option><option value="m">Metro (m)</option>
                        </optgroup>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Qtd Estoque * {INTEIRAS.includes(form.unidade_medida)?'(inteiro)':'(decimal)'}</label>
                      <input className="input" type="number" required step={INTEIRAS.includes(form.unidade_medida)?'1':'0.001'} value={form.quantidade_estoque} onChange={f('quantidade_estoque')}/>
                    </div>
                    <div>
                      <label className="form-label">Estoque Mínimo</label>
                      <input className="input" type="number" step={INTEIRAS.includes(form.unidade_medida)?'1':'0.001'} value={form.estoque_minimo} onChange={f('estoque_minimo')}/>
                    </div>
                    <div>
                      <label className="form-label">Categoria</label>
                      <select className="input" value={form.categoria} onChange={f('categoria')}>
                        <option value="">Sem categoria</option>
                        {categorias.map(c=><option key={c.id} value={c.id}>{c.nome}</option>)}
                      </select>
                    </div>
                    <div style={{gridColumn:'1/-1'}}><label className="form-label">Descrição</label><textarea className="input" rows={2} value={form.descricao} style={{resize:'none'}} onChange={f('descricao')}/></div>
                  </div>
                  <div className="actions-row mt-16" style={{justifyContent:'flex-end'}}>
                    <button type="button" className="btn btn-muted" onClick={()=>setShowForm(false)}>Cancelar</button>
                    <button type="submit" className="btn btn-primary">{editando?'Salvar':'Criar Produto'}</button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Modal Categoria */}
          {showCat && (
            <div className="modal-overlay">
              <div style={{background:'var(--card)',borderRadius:20,padding:28,width:'min(440px,94vw)',border:'1px solid var(--border)',boxShadow:'var(--shadow)'}}>
                <div className="modal-header">
                  <span className="modal-title">{editCat?'✏️ Editar Categoria':'+ Nova Categoria'}</span>
                  <button className="modal-close" onClick={()=>setShowCat(false)}>×</button>
                </div>
                <form onSubmit={salvarCat}>
                  <div className="form-row"><label className="form-label">Nome *</label><input className="input" value={formCat.nome} required onChange={fc('nome')}/></div>
                  <div className="form-row"><label className="form-label">Descrição</label><input className="input" value={formCat.descricao} onChange={fc('descricao')}/></div>
                  <div className="actions-row mt-16" style={{justifyContent:'flex-end'}}>
                    <button type="button" className="btn btn-muted" onClick={()=>setShowCat(false)}>Cancelar</button>
                    <button type="submit" className="btn btn-primary">{editCat?'Salvar':'Criar'}</button>
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
