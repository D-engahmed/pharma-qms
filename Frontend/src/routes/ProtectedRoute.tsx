import type { ReactNode } from 'react';
export function ProtectedRoute({ authenticated, children }: { authenticated: boolean; children: ReactNode }) {
  return authenticated ? <>{children}</> : null;
}
