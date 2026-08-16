export function Detail({ title, rows }: any) {
  return <section className="detail-section"><h4>{title}</h4><div className="detail-grid">{rows.map(([k,v]: any) => <div key={k}><span>{k}</span><b>{v || '—'}</b></div>)}</div></section>;
}
