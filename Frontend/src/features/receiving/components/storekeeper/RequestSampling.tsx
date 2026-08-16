import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function RequestSampling({m,close,state,update,notify}) {
  if(!m) return null;
  const submit=()=>{update(s=>{const x=s.materials.find(x=>x.id===m.id); if(x) x.samplingStatus="Sampling Requested"});close();notify("Sampling request submitted!")};
  return <Modal title="Confirm Sampling Request" sub="Verify details before submitting" open onClose={close} footer={<><Button onClick={close}>Cancel</Button><Button variant="primary" onClick={submit}>✓ Submit Request</Button></>}><div className="confirm-info"><div className="confirm-row"><span>Material Name</span><b>{m.materialName}</b></div><div className="confirm-row"><span>Receipt ID</span><b className="mono">{m.receiptId}</b></div><div className="confirm-row"><span>Supplier Batch No.</span><b>{m.supplierBatch}</b></div><div className="confirm-row"><span>Supplier</span><b>{m.supplier||"—"}</b></div><div className="confirm-row"><span>Total Quantity</span><b>{m.totalQty||"—"} {m.unit||""}</b></div></div><p className="confirm-note">Submitting will update sampling status to <strong>Sampling Requested</strong>.</p></Modal>
}
