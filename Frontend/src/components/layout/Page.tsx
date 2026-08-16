export function Page({title,sub,action,children}) { return <main className="main-content"><div className="page-header"><div><h2>{title}</h2><p>{sub}</p></div>{action}</div>{children}</main> }
