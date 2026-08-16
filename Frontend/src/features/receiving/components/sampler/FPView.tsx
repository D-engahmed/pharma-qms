import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function FPView({f,close}) { return <Modal title={f.productName} sub={`${f.sampleId} · ${f.productType}`} open onClose={close} footer={<Button onClick={close}>Close</Button>}><Detail title="Product & Sample Details" rows={[["Product Name",f.productName],["Product Type",f.productType],["Batch No.",f.batchNo],["Batch Size",`${f.batchSize} ${f.unit||""}`],["Manufacturing",fmt(f.mfgDate)],["Expiry",fmt(f.expDate)],["Sample Qty",`${f.sampleSize} ${f.unit||""}`],["Sampling Date",fmt(f.samplingDate)],["Time",f.timeOfSampling]]}/><Detail title="Stage" rows={[["Selected",f.stages?.join(", ")||"No stage selected"]]}/><Detail title="Testing Status" rows={[["Status",<Status value={f.testingStatus}/>]]}/></Modal> }
