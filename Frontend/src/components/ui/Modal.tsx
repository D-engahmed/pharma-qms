export function Modal({title,sub,open,onClose,children,footer,wide=false}) {
  if(!open) return null;
  return <div className="overlay" onMouseDown={e=>e.target===e.currentTarget&&onClose()}>
    <div className={`modal ${wide?"modal-lg":""}`}>
      <header className="modal-header"><div><div className="modal-title">{title}</div>{sub&&<div className="modal-sub">{sub}</div>}</div><button className="modal-close" onClick={onClose}>×</button></header>
      <div className="modal-body">{children}</div>
      {footer && <footer className="modal-footer">{footer}</footer>}
    </div>
  </div>
}
