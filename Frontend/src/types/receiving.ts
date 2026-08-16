export type UserRole = 'storekeeper' | 'sampler' | 'analyst' | 'qcmanager';
export type MaterialStatus = 'Quarantine' | 'Released' | 'Rejected';
export type SamplingStatus = 'Not Sampled' | 'Sampling Requested' | 'Sampled';
export type TestingStatus = 'Not Tested' | 'In Testing' | 'Completed';
export type COAStatus = 'Draft' | 'In Progress' | 'Completed' | 'Approved' | 'Rejected';

export interface Material { id: string; receiptId: string; materialName: string; supplier?: string; manufacturer?: string; supplierBatch?: string; status: MaterialStatus; samplingStatus: SamplingStatus; [key: string]: unknown; }
export interface Sample { id: string; sampleId: string; materialName?: string; receiptId?: string; testingStatus: TestingStatus; [key: string]: unknown; }
export interface Packaging { id: string; receiptId: string; name: string; [key: string]: unknown; }
export interface COA { id: string; sampleId: string; status: COAStatus; sampleName: string; [key: string]: unknown; }
export interface ReceivingState { materials: Material[]; samples: Sample[]; packagings: Packaging[]; fpSamples: any[]; coas: COA[]; notifications: any[]; counters: Record<string, number>; opts: Record<string, string[]>; }
