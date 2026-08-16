import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function Release({c,close,state,update,notify,open}) {
  const [qc,setQc]=useState(""),[sign,setSign]=useState("");const submit=()=>{if(!qc||!sign)return notify("QC Number and Signature are required.","error");const ret=new Date();ret.setFullYear(ret.getFullYear()+1);const retest=ret.toISOString().slice(0,10);update(s=>{const coa=s.coas.find(x=>x.id===c.id);const m=s.materials.find(x=>x.id===coa?.materialId);if(m){m.status="Released";m.qcNumber=qc;m.qcSign=sign;m.retestDate=retest;m.releasedDate=today();s.notifications.push({id:"N-"+Date.now(),read:false,title:`Material Released: ${coa.sampleName}`,message:`Receipt ID: ${coa.receiptId} · QC No: ${qc} · Retest by: ${fmt(retest)}`})}});close();notify("Material released! Storekeeper has been notified.")};
  return <Modal title="Release Material" sub="COA approved — assign QC number to release" open onClose={close} footer={<><Button onClick={close}>Cancel</Button><Button variant="primary" onClick={submit}>✓ Release Material</Button></>}><div className="release-highlight"><b>{c.sampleName}</b><small>Receipt: {c.receiptId} · Batch: {c.batchNo}</small></div><Field label="QC Number *"><Input value={qc} onChange={setQc} placeholder="QC-2026-0001"/></Field><Field label="QC Manager Signature *"><Input value={sign} onChange={setSign} placeholder="Full name / signature"/></Field><p className="confirm-note">Retest date is automatically set to release date + 1 year.</p></Modal>
}
