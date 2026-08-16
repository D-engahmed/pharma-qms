export function Empty({ text = 'No records found.' }) {
  return <div className="empty-state"><div className="empty-icon">📋</div><div className="empty-title">{text}</div></div>;
}
