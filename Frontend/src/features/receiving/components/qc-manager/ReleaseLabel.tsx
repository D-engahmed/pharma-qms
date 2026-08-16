import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function ReleaseLabel({m,close,state}) {
  const s=state.samples.find(x=>x.materialId===m.id);return <Modal title="Release Label" sub={`${m.receiptId} · ${m.materialName}`} open onClose={close} footer={<><Button onClick={close}>Close</Button><Button variant="purple" onClick={()=>window.print()}>🖨 Print Release Label</Button></>}><div className="label-wrap"><div className="label-card"><header className="purple-head">✓ RELEASED — QC APPROVED</header><div className="label-body"><h4>RELEASED MATERIAL LABEL</h4>{[["Receipt ID",m.receiptId],["Material Name",m.materialName],["Batch No.",m.supplierBatch],["Batch Size",`${m.batchSize||"—"} ${m.unit||""}`],["Supplier",m.supplier],["Mfg Date",fmt(m.mfgDate)],["Exp Date",fmt(m.expDate)],["Container No.",s?.containers],["QC Number",m.qcNumber],["Storage",s?.storage||m.storageCondition],["Retest Date",fmt(m.retestDate)],["QC Signature",m.qcSign],["Release Date",fmt(m.releasedDate)]].map(x=><div className="lrow" key={x[0]}><span>{x[0]}</span><b>{x[1]||"—"}</b></div>)}</div></div></div></Modal>
}
