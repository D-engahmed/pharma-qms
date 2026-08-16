import type { ReceivingState } from '../../../types/receiving';
export const STORAGE_KEY = 'rm-receiving-state';
export const initialReceivingState: ReceivingState = {
  materials: [], samples: [], packagings: [], fpSamples: [], coas: [], notifications: [],
  counters: { rc:1, pkg:1, fp:1, sfp:1, blk:1, coa:1 },
  opts: {
    materialName:["Paracetamol","Ibuprofen","Amoxicillin","Metformin","Aspirin"],
    category:["API","Excipient","Packaging Material","Solvent","Reagent"],
    supplier:["PharmaChem Ltd","BioSource Inc","EuroChem GmbH","AsiaMed Co."],
    manufacturer:["BASF SE","DSM Nutritional","Lonza Group","Evonik Industries"],
    unit:["kg","g","mg","L","mL","tablets","capsules"],
    packageType:["Drum","Bag","Carton","Bottle","Pail","IBC"],
    warehouse:["WH-01 (Cold Storage)","WH-02 (Ambient)","WH-03 (Flammables)","WH-04 (General)"],
    productName:["Paracetamol 500mg Tablet","Amoxicillin 250mg Capsule","Ibuprofen 400mg Tablet","Metformin 500mg Tablet"]
  }
};
export function loadReceivingState(): ReceivingState { try { const raw=localStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : structuredClone(initialReceivingState); } catch { return structuredClone(initialReceivingState); } }
export function saveReceivingState(state: ReceivingState) { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
