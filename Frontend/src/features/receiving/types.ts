export * from '../../types/receiving';

export type ReceivingModal =
  | 'register'
  | 'packaging'
  | 'requestSampling'
  | 'materialView'
  | 'sampling'
  | 'label'
  | 'fpView'
  | 'packagingView'
  | 'coaForm'
  | 'coaView'
  | 'qcm'
  | 'release'
  | 'releaseLabel'
  | `fp:${string}`
  | null;
