import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function LabelModal({s,close}) {
  if(!s)return null;
  return <Modal title="Label Preview" sub={`Sample ID: ${s.sampleId} · ${s.materialName}`} open onClose={close} footer={<><Button onClick={close}>Close</Button><Button variant="info" onClick={()=>window.print()}>🖨 Print Labels</Button></>}><div className="label-wrap"><div className="label-card"><header>🛡 Sample Label</header><div className="label-body"><h4>QC SAMPLE</h4>{[["Sample ID",s.sampleId],["Material",s.materialName],["Supplier",s.supplier],["Supplier Batch",s.supplierBatch],["Sample Size",`${s.sampleSize} ${s.unit}`],["Storage",s.storage],["Sampling Date",fmt(s.samplingDate)],["Expiry Date",fmt(s.expDate)],["Sampled By",s.sampler]].map(x=><div className="lrow" key={x[0]}><span>{x[0]}</span><b>{x[1]||"—"}</b></div>)}</div></div><div className="label-card"><header>▣ Sampled Container</header><div className="label-body"><h4>SAMPLED — QUARANTINE</h4>{[["Receipt ID",s.receiptId],["Material",s.materialName],["Manufacturer",s.manufacturer],["Supplier Batch",s.supplierBatch],["Containers",s.containers],["Sample Taken",`${s.sampleSize} ${s.unit}`],["Sampling Date",fmt(s.samplingDate)],["Location",s.location],["Sampled By",s.sampler]].map(x=><div className="lrow" key={x[0]}><span>{x[0]}</span><b>{x[1]||"—"}</b></div>)}</div></div></div></Modal>
}
