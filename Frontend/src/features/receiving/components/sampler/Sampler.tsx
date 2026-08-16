import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { ProductSamples } from './ProductSamples';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function Sampler({state,update,notify,tab,setTab,search,setSearch,open,setSelected}) {
  const requested=state.materials.filter(m=>m.samplingStatus==="Sampling Requested").filter(m=>!search||`${m.materialName} ${m.receiptId} ${m.supplierBatch}`.toLowerCase().includes(search.toLowerCase()));
  return <>
    <Tabs value={tab} onChange={x=>{setTab(x);setSearch("")}} items={[["requests","◷ Sampling Requests",state.materials.filter(m=>m.samplingStatus==="Sampling Requested").length],["history","▤ Sample History"],["fpsamples","⌑ Product Samples"],["prodhistory","▤ Product Sample History"]]}/>
    {tab==="requests"&&<Page title="Sampling Requests" sub="Materials awaiting sampling action"><div className="pending-banner"><strong>{requested.length}</strong><div><b>Total Pending Sampling Requests</b><small>Materials with “Sampling Requested” status require your action</small></div></div><div className="table-card"><Toolbar search={search} setSearch={setSearch}/><Table headers={["Receipt ID","Material","Batch","Receiving Date","Qty","Status","Sampling","Expire","Containers","Actions"]}>{requested.map(m=><tr key={m.id}><td className="mono">{m.receiptId}</td><td><b>{m.materialName}</b></td><td>{m.supplierBatch}</td><td>{fmt(m.receiptDate)}</td><td>{m.totalQty} {m.unit}</td><td><Status value={m.status}/></td><td><Status value={m.samplingStatus}/></td><td>{fmt(m.expDate)}</td><td>{m.numPackages||"—"}</td><td><Button small onClick={()=>{setSelected(m);open("sampling")}}>Sample</Button></td></tr>)}</Table></div></Page>}
    {tab==="history"&&<Page title="Sample History" sub="All recorded samples — reprint labels anytime"><div className="table-card"><Toolbar search={search} setSearch={setSearch}/><Table headers={["Sample ID","Material","Receipt ID","Batch","Sample Size","Containers","Sampler","Date","Storage","Actions"]}>{state.samples.filter(s=>!search||`${s.materialName} ${s.sampleId} ${s.supplierBatch}`.toLowerCase().includes(search.toLowerCase())).map(s=><tr key={s.id}><td className="mono">{s.sampleId}</td><td>{s.materialName}</td><td>{s.receiptId}</td><td>{s.supplierBatch}</td><td>{s.sampleSize} {s.unit}</td><td>{s.containers}</td><td>{s.sampler}</td><td>{fmt(s.samplingDate)}</td><td>{s.storage}</td><td><Button small variant="info" onClick={()=>{setSelected(s);open("label")}}>Print Labels</Button></td></tr>)}</Table></div></Page>}
    {(tab==="fpsamples"||tab==="prodhistory")&&<ProductSamples state={state} update={update} notify={notify} history={tab==="prodhistory"} open={open} setSelected={setSelected} search={search} setSearch={setSearch}/>}
  </>
}
