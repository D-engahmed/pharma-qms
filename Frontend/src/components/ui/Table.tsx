import React from "react";
export function Table({headers,children,empty}) {
  return <div className="table-card"><div className="table-wrap"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{children}</tbody></table></div>{!children || React.Children.count(children)===0 ? <Empty text={empty}/> : null}</div>
}
