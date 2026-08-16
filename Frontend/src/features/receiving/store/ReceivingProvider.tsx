import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { deepClone } from '../../../utils';
import { loadReceivingState, saveReceivingState } from '../services/receivingStorage';

const ReceivingContext = createContext<any>(null);

export function ReceivingProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState(loadReceivingState);
  const [toast, setToast] = useState<any>(null);
  useEffect(() => saveReceivingState(state), [state]);
  useEffect(() => { if (!toast) return; const timer = setTimeout(() => setToast(null), 3500); return () => clearTimeout(timer); }, [toast]);
  const value = useMemo(() => ({
    state,
    update: (fn: (draft: any) => void) => setState((current: any) => { const next = deepClone(current); fn(next); return next; }),
    notify: (msg: string, type = 'success') => setToast({ msg, type }),
    toast,
  }), [state, toast]);
  return <ReceivingContext.Provider value={value}>{children}</ReceivingContext.Provider>;
}

export const useReceiving = () => { const ctx = useContext(ReceivingContext); if (!ctx) throw new Error('useReceiving must be used inside ReceivingProvider'); return ctx; };
