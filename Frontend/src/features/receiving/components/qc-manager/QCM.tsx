import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function QCM({c,close,open,state,update,notify}) {
  const [comment,setComment]=useState(""); return <Modal title={c.status==="Completed"?"Review COA":"COA Review"} sub={`${c.id} · ${c.sampleName}`} open onClose={close} footer={<><Button onClick={close}>Cancel</Button><Button variant="danger" onClick={()=>{update(s=>{const x=s.coas.find(x=>x.id===c.id);x.status="Rejected";x.qcManagerComment=comment;const m=s.materials.find(m=>m.id===x.materialId);if(m)m.status="Rejected"});close();notify("COA rejected","error")}}>Reject</Button><Button variant="primary" onClick={()=>{update(s=>{const x=s.coas.find(x=>x.id===c.id);x.status="Approved";x.qcManagerComment=comment});close();open("release");notify("COA approved")}}>Approve COA</Button></>}><Detail title="COA" rows={[["COA ID",c.id],["Sample",c.sampleName],["Batch",c.batchNo],["Analyst",c.analyst]]}/><Field label="QC Manager Comments"><textarea value={comment} onChange={e=>setComment(e.target.value)} placeholder="Optional comments…"/></Field></Modal>
}
