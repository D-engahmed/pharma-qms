import { useState } from 'react';
import { Badge, Status, Button, Modal, Field, Input, Select, Table, Empty } from '../../../../components/ui';
import { Tabs, Page, Toolbar } from '../../../../components/layout';
import { Detail } from '../shared/Detail';
import { formatDate as fmt, today, createDocumentId as id } from '../../../../utils';
export function PackagingView({p,close}) { return <Modal title={p.name} sub={`${p.receiptId} · ${p.supplier}`} open onClose={close} footer={<Button onClick={close}>Close</Button>}><Detail title="Packaging Details" rows={[["Name",p.name],["Type",p.type],["Quantity",`${p.qty} ${p.unit||""}`],["Supplier",p.supplier],["PO No.",p.po],["Warehouse",p.warehouse],["Receipt Date",fmt(p.receiptDate)],["Recipient",p.recipient]]}/>{p.description&&<Detail title="Description" rows={[["Description",p.description]]}/>}</Modal> }
