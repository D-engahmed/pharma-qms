import { useState } from 'react';
import { Button } from '../../../components/ui';

const roleInfo: Record<string, [string,string,string]> = {
  storekeeper:['📦','Storekeeper','Register & manage materials'],
  sampler:['🔬','Sampler','Sampling requests & labels'],
  analyst:['🧪','Analyst','Testing & certificates'],
  qcmanager:['✅','QC Manager','Approve COAs & release']
};
export function Login({role,setRole}) {
  const [selectedRole,setSelectedRole]=useState(null);
  return <main className="login-screen"><div className="login-card">
    <div className="login-logo">⌬</div><h1>RM Receiving System</h1>
    <p>Raw Material Receiving & Sampling · GMP Prototype</p>
    <div className="login-label">Select Your Role</div>
    <div className="role-cards">{Object.entries(roleInfo).map(([k,[icon,name,desc]])=><button key={k} className={`role-card ${selectedRole===k?"selected":""}`} onClick={()=>setSelectedRole(k)}><span>{icon}</span><div><strong>{name}</strong><small>{desc}</small></div></button>)}</div>
    <Button variant="primary" disabled={!selectedRole} onClick={()=>setRole(selectedRole)}>Continue as {selectedRole?roleInfo[selectedRole][1]:"Select a role to continue"}</Button>
  </div></main>
}
