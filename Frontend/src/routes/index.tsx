import { Login } from '../features/auth';
import { ReceivingModule } from '../features/receiving/ReceivingModule';
import type { UserRole } from '../types/receiving';

export function AppRouter({ role, setRole }: { role: UserRole | null; setRole: (role: UserRole | null) => void }) {
  return role ? <ReceivingModule role={role} onLogout={() => setRole(null)} /> : <Login role={role} setRole={setRole} />;
}
