import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function MaterialView({m,close,open,state,update,notify}) {
  if(!m)return null;
  return <Modal title={m.materialName} sub={`${m.receiptId} · ${m.supplier}`} open onClose={close} footer={<><Button onClick={close}>Close</Button>{m.samplingStatus==="Not Sampled"&&<Button variant="primary" onClick={()=>open("requestSampling")}>Request Sampling</Button>}</>}><Detail title="Material Information" rows={[["Material Name",m.materialName],["Category",m.category],["Supplier",m.supplier],["Manufacturer",m.manufacturer],["Country",m.countryOrigin],["Supplier Batch",m.supplierBatch]]}/><Detail title="Dates & Batch" rows={[["Manufacturing",fmt(m.mfgDate)],["Expiry",fmt(m.expDate)],["Batch Size",`${m.batchSize||"—"} ${m.unit||""}`]]}/><Detail title="Packaging" rows={[["Package Type",m.packageType],["Packages",m.numPackages],["Package Size",m.packageSize],["Total Qty",`${m.totalQty||"—"} ${m.unit||""}`]]}/><Detail title="Status" rows={[["Material",<Status value={m.status}/>],["Sampling",<Status value={m.samplingStatus}/>]]}/>{state&&<RequestSamplingInline m={m} close={close} state={state} update={update} notify={notify} open={open}/>}</Modal>
}
