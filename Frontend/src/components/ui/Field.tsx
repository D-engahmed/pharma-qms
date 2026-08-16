export function Field({label,children,full=false}) { return <div className={`form-group ${full?"form-full":""}`}><label>{label}</label>{children}</div> }
