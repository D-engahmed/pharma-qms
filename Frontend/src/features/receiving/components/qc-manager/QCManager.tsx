import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function QCManager({state,update,notify,search,setSearch,open,setSelected}) {
  const rows=state.coas.filter(c=>!search||`${c.sampleName} ${c.receiptId} ${c.batchNo}`.toLowerCase().includes(search.toLowerCase()));
  return <Page title="COA Review & Approval" sub="Review completed certificates and approve or reject"><div className="table-card"><Toolbar search={search} setSearch={setSearch}/><Table headers={["Receipt ID","Sample Name","Batch No.","Analyst","Created Date","Status","Actions"]}>{rows.map(c=><tr key={c.id}><td>{c.receiptId}</td><td>{c.sampleName}</td><td>{c.batchNo}</td><td>{c.analyst}</td><td>{fmt(c.createdDate)}</td><td><Status value={c.status}/></td><td><Button small onClick={()=>{setSelected(c);open("coaView")}}>View</Button>{c.status==="Completed"&&<Button small variant="primary" onClick={()=>{setSelected(c);open("qcm")}}>Review</Button>}</td></tr>)}</Table></div></Page>
}
