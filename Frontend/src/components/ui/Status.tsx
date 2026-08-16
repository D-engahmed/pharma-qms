export function Status({value}) {
  const map={Quarantine:"quarantine",Released:"released",Rejected:"rejected","Not Sampled":"notsampled","Sampling Requested":"requested",Sampled:"sampled","Not Tested":"nottested","In Testing":"intesting",Completed:"completed",Approved:"approved",Draft:"draft","In Progress":"inprogress"};
  return <Badge kind={map[value]||"notsampled"}>{value || "—"}</Badge>
}
