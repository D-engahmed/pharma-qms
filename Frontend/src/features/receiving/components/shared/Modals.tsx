import { RegisterMaterial } from '../storekeeper/RegisterMaterial';
import { RegisterPackaging } from '../storekeeper/RegisterPackaging';
import { MaterialView } from '../storekeeper/MaterialView';
import { RequestSampling } from '../storekeeper/RequestSampling';
import { Sampling } from '../sampler/Sampling';
import { LabelModal } from '../sampler/LabelModal';
import { FPView } from '../sampler/FPView';
import { FPForm } from '../sampler/FPForm';
import { PackagingView } from '../storekeeper/PackagingView';
import { COAForm } from '../analyst/COAForm';
import { COAView } from '../analyst/COAView';
import { QCM } from '../qc-manager/QCM';
import { Release } from '../qc-manager/Release';
import { ReleaseLabel } from '../qc-manager/ReleaseLabel';

export function Modals({ modal, setModal, state, update, notify, selected, setSelected }: any) {
  const close = () => { setModal(null); setSelected?.(null); };
  if (modal === 'register') return <RegisterMaterial close={close} state={state} update={update} notify={notify}/>;
  if (modal === 'packaging') return <RegisterPackaging close={close} state={state} update={update} notify={notify}/>;
  if (modal === 'requestSampling') return <RequestSampling m={selected} close={close} state={state} update={update} notify={notify}/>;
  if (modal === 'materialView') return <MaterialView m={selected} close={close} open={setModal} state={state} update={update} notify={notify}/>;
  if (modal === 'sampling') return <Sampling m={selected} close={close} state={state} update={update} notify={notify} open={setModal}/>;
  if (modal === 'label') return <LabelModal s={selected} close={close}/>;
  if (modal === 'fpView') return <FPView f={selected} close={close}/>;
  if (modal?.startsWith('fp:')) return <FPForm type={modal.slice(3)} close={close} state={state} update={update} notify={notify}/>;
  if (modal === 'packagingView') return <PackagingView p={selected} close={close}/>;
  if (modal === 'coaForm') return <COAForm sample={selected} close={close} state={state} update={update} notify={notify}/>;
  if (modal === 'coaView') return <COAView c={selected} close={close} open={setModal} state={state} update={update} notify={notify}/>;
  if (modal === 'qcm') return <QCM c={selected} close={close} open={setModal} state={state} update={update} notify={notify}/>;
  if (modal === 'release') return <Release c={selected} close={close} state={state} update={update} notify={notify} open={setModal}/>;
  if (modal === 'releaseLabel') return <ReleaseLabel m={selected} close={close} state={state}/>;
  return null;
}
