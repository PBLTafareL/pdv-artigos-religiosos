export default function Modal({ title, onClose, children, width = '680px' }) {
  return (
    <div className="modal-overlay" onClick={e => e.target===e.currentTarget && onClose()}>
      <div className="modal-box" style={{ width: `min(${width},94vw)` }}>
        <div className="modal-header">
          <span className="modal-title">{title}</span>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        {children}
      </div>
    </div>
  )
}
