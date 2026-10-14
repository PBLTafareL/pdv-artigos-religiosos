import { useState } from 'react'
const FORMAS = [
  { v:'dinheiro',       l:'💵 Dinheiro' },
  { v:'pix',            l:'📱 PIX' },
  { v:'cartao_debito',  l:'💳 Débito' },
  { v:'cartao_credito', l:'💳 Crédito' },
  { v:'pontos',         l:'🏆 Pontos' },
]
export default function Pagamento({ total, clientePontos=0, onPagar, onClose }) {
  const [forma,  setForma]  = useState('dinheiro')
  const [valor,  setValor]  = useState(total.toFixed(2))
  const [pontos, setPontos] = useState(0)
  const [chPix,  setChPix]  = useState('')
  const troco = forma==='dinheiro' ? Math.max(0, parseFloat(valor||0)-total) : 0
  const confirmar = () => onPagar({ forma_pagamento:forma, valor:parseFloat(valor||total), pontos_resgate:pontos, chave_pix:chPix })
  return (
    <div className="modal-overlay">
      <div style={{ background:'var(--card)',borderRadius:20,padding:28,width:'min(420px,94vw)',border:'1px solid var(--border)',boxShadow:'var(--shadow)' }}>
        <div className="modal-header"><span className="modal-title">Pagamento</span><button className="modal-close" onClick={onClose}>×</button></div>
        <div style={{ textAlign:'center',marginBottom:20 }}>
          <p style={{ fontSize:13,opacity:.7,marginBottom:4 }}>Total a pagar</p>
          <p style={{ fontSize:32,fontWeight:800,color:'var(--accent)' }}>R$ {total.toFixed(2)}</p>
        </div>
        <div style={{ display:'grid',gridTemplateColumns:'1fr 1fr',gap:8,marginBottom:16 }}>
          {FORMAS.map(f => (
            <button key={f.v} onClick={() => setForma(f.v)} style={{
              padding:'10px 8px',borderRadius:10,fontSize:13,fontWeight:700,cursor:'pointer',
              background: forma===f.v ? 'var(--accent)' : 'var(--muted)',
              color: forma===f.v ? '#fff' : 'var(--text)',
              border: forma===f.v ? '2px solid var(--accent)' : '2px solid var(--border)',
            }}>{f.l}</button>
          ))}
        </div>
        {forma==='dinheiro' && (
          <div style={{ marginBottom:12 }}>
            <label className="form-label">Valor recebido (R$)</label>
            <input type="number" className="input" value={valor} onChange={e=>setValor(e.target.value)} step=".01" min={total} />
            {troco>0 && <p style={{ color:'var(--accent)',fontWeight:700,marginTop:6 }}>💰 Troco: R$ {troco.toFixed(2)}</p>}
          </div>
        )}
        {forma==='pix' && (
          <div style={{ marginBottom:12 }}>
            <label className="form-label">Chave PIX</label>
            <input className="input" value={chPix} onChange={e=>setChPix(e.target.value)} placeholder="CPF, e-mail, telefone..." />
          </div>
        )}
        {forma==='pontos' && (
          <div style={{ marginBottom:12 }}>
            <label className="form-label">Pontos a resgatar (Saldo: {clientePontos})</label>
            <input type="number" className="input" value={pontos} onChange={e=>setPontos(parseInt(e.target.value)||0)} min={0} max={clientePontos} />
          </div>
        )}
        <div style={{ display:'flex',gap:8,marginTop:8 }}>
          <button className="btn btn-muted" style={{ flex:1,justifyContent:'center' }} onClick={onClose}>Cancelar</button>
          <button className="btn btn-accent" style={{ flex:1,justifyContent:'center' }} onClick={confirmar}>✅ Confirmar</button>
        </div>
      </div>
    </div>
  )
}
