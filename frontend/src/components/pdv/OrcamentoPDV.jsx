import { useState } from 'react'
export default function OrcamentoPDV({ onSalvar, onClose }) {
  const [validade, setValidade] = useState('')
  const [obs, setObs] = useState('')
  const amanha = new Date(); amanha.setDate(amanha.getDate()+1)
  const minDate = amanha.toISOString().split('T')[0]
  return (
    <div className="modal-overlay">
      <div style={{ background:'var(--card)',borderRadius:20,padding:28,width:'min(420px,94vw)',border:'1px solid var(--border)',boxShadow:'var(--shadow)' }}>
        <div className="modal-header"><span className="modal-title">💰 Salvar como Orçamento</span><button className="modal-close" onClick={onClose}>×</button></div>
        <div className="form-row">
          <label className="form-label">Válido até *</label>
          <input type="date" className="input" value={validade} onChange={e=>setValidade(e.target.value)} min={minDate} />
        </div>
        <div className="form-row">
          <label className="form-label">Observação (opcional)</label>
          <textarea className="input" rows={3} value={obs} onChange={e=>setObs(e.target.value)} style={{ resize:'none' }} />
        </div>
        <div style={{ display:'flex',gap:8,marginTop:16 }}>
          <button className="btn btn-muted" style={{ flex:1,justifyContent:'center' }} onClick={onClose}>Cancelar</button>
          <button className="btn btn-primary" style={{ flex:1,justifyContent:'center' }} onClick={() => onSalvar({validade,observacao:obs})} disabled={!validade}>Salvar</button>
        </div>
      </div>
    </div>
  )
}
