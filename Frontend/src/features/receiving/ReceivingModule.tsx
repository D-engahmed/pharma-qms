import { useState } from 'react';
import { useReceiving } from './store/ReceivingProvider';
import { Storekeeper } from './components/storekeeper/Storekeeper';
import { Sampler } from './components/sampler/Sampler';
import { Analyst } from './components/analyst/Analyst';
import { QCManager } from './components/qc-manager/QCManager';
import { Modals } from './components/shared/Modals';
const roleInfo: Record<string, [string,string,string]> = {
  storekeeper: ['📦','Storekeeper','Register & manage materials'],
  sampler: ['🔬','Sampler','Sampling requests & labels'],
  analyst: ['🧪','Analyst','Testing & certificates'],
  qcmanager: ['✅','QC Manager','Approve COAs & release']
};
import type { UserRole } from '../../types/receiving';

export function ReceivingModule({ role, onLogout }: { role: UserRole; onLogout: () => void }) {
  const { state, update, notify, toast } = useReceiving();
  const [skTab,setSkTab]=useState('materials'); const [smTab,setSmTab]=useState('requests'); const [analystPage,setAnalystPage]=useState('home');
  const [modal,setModal]=useState<any>(null); const [selected,setSelected]=useState<any>(null); const [search,setSearch]=useState('');
  const addOption=(key:string,val:string)=>val.trim()&&update((s:any)=>{if(!s.opts[key].includes(val.trim()))s.opts[key].push(val.trim())});
  return <div className="app">
    <header className="topbar"><div className="brand"><div className="logo">⌬</div>RM Receiving System</div><div className="spacer"/><div className="role-pill">{roleInfo[role][0]} {roleInfo[role][1]}</div>{role==='storekeeper'&&<button className="icon-btn" onClick={()=>notify(state.notifications.length?'Notifications available':'No new notifications','info')}>♧{state.notifications.filter((n:any)=>!n.read).length?` ${state.notifications.filter((n:any)=>!n.read).length}`:''}</button>}<button className="btn btn-secondary" onClick={onLogout}>Logout</button></header>
    {role==='storekeeper'&&<Storekeeper state={state} update={update} notify={notify} tab={skTab} setTab={setSkTab} search={search} setSearch={setSearch} open={setModal} selected={selected} setSelected={setSelected} addOption={addOption}/>}
    {role==='sampler'&&<Sampler state={state} update={update} notify={notify} tab={smTab} setTab={setSmTab} search={search} setSearch={setSearch} open={setModal} setSelected={setSelected}/>}
    {role==='analyst'&&<Analyst state={state} update={update} notify={notify} page={analystPage} setPage={setAnalystPage} search={search} setSearch={setSearch} open={setModal} setSelected={setSelected}/>}
    {role==='qcmanager'&&<QCManager state={state} update={update} notify={notify} search={search} setSearch={setSearch} open={setModal} setSelected={setSelected}/>}
    <Modals modal={modal} setModal={setModal} state={state} update={update} notify={notify} selected={selected} setSelected={setSelected}/>{toast&&<div className={`toast ${toast.type}`}><b>{toast.type==='error'?'✕':toast.type==='info'?'ℹ':'✓'}</b>{toast.msg}</div>}
  </div>;
}
