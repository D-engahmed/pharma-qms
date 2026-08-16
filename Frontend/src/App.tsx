import { useState } from 'react';
import { ReceivingProvider } from './features/receiving/store/ReceivingProvider';
import { AppRouter } from './routes';
import type { UserRole } from './types/receiving';

export default function App() {
  const [role, setRole] = useState<UserRole | null>(null);
  return <ReceivingProvider><AppRouter role={role} setRole={setRole}/></ReceivingProvider>;
}
