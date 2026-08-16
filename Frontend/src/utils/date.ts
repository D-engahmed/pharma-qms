export const today = () => new Date().toISOString().slice(0, 10);
export const formatDate = (value?: string) => value ? value.split('-').reverse().join('/') : '—';
export const createDocumentId = (prefix: string, counter: number) => `${prefix}-${new Date().getFullYear()}-${String(counter).padStart(4, '0')}`;
