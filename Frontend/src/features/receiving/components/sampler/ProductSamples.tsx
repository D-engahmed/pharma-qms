import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function ProductSamples({state,update,notify,history,open,setSelected,search,setSearch}) {
  const rows=state.fpSamples.filter(x=>!search||`${x.productName} ${x.sampleId} ${x.batchNo}`.toLowerCase().includes(search.toLowerCase()));
  return <Page title={history?"Product Sample History":"Product Samples"} sub={history?"All registered FP / SFP / Bulk samples":"Register finished product, semi-finished and bulk samples"} action={!history&&<div className="action-group"><Button variant="primary" onClick={()=>open("fp:Finished Product")}>＋ Finished Product</Button><Button variant="info" onClick={()=>open("fp:Semi-Finished Product")}>＋ Semi-Finished Product</Button><Button onClick={()=>open("fp:Bulk")}>＋ Bulk</Button></div>}>
    <div className="table-card"><Toolbar search={search} setSearch={setSearch}/><Table headers={["Sample ID","Product","Type","Batch","Batch Size","Sample Qty","Mfg Date","Exp Date","Sampling Date","Testing","Actions"]}>{rows.map(f=><tr key={f.id}><td className="mono">{f.sampleId}</td><td><b>{f.productName}</b></td><td><Badge kind={f.productType==="Finished Product"?"fp":f.productType==="Semi-Finished Product"?"sfp":"bulk"}>{f.productType}</Badge></td><td>{f.batchNo}</td><td>{f.batchSize} {f.unit}</td><td>{f.sampleSize} {f.unit}</td><td>{fmt(f.mfgDate)}</td><td>{fmt(f.expDate)}</td><td>{fmt(f.samplingDate)}</td><td><Status value={f.testingStatus}/></td><td><Button small onClick={()=>{setSelected(f);open("fpView")}}>View</Button></td></tr>)}</Table></div>
  </Page>
}
