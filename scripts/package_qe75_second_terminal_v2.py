"""Package offline corrections to AC-stopped second attempt; preserve original."""
from pathlib import Path
import hashlib,json,zipfile,time
R=Path(__file__).resolve().parents[1];E=R/'evidence/qe75-second-v6'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 old=R/'artifacts/phase3/uio66_qe_water_pair_v6_windows.zip';dest=old.with_name('uio66_qe_water_pair_v6_windows_v2.zip')
 original='dfad6357c3750de08dae0e020985bc590881be69dfbd30f623f11e2a20cffbd3';assert sha(old)==original
 extras={}
 for n in ['assessment-terminal-v2.json','partial-independent-audit.json','postflight-followup.json','portable-review-receipt.json','finalization-complete.json']:extras['evidence/'+n]=E/n
 for n in ['audit_qe75_second_partial_v6.py','package_qe75_second_terminal_v2.py']:extras['controller/'+n]=R/'scripts'/n
 extras['REVIEW_REPORT.md']=R/'docs/UIO66_QE75_SECOND_V6_RESULTS.md';extras['updated-execution-config.json']=R/'configs/qe75-second-v6.json'
 hashes={}
 with zipfile.ZipFile(old) as src,zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as out:
  previous=json.loads(src.read('SHA256SUMS.json'))
  for info in src.infolist():
   if info.is_dir():continue
   n=info.filename;new={'REVIEW_REPORT.md':'original-automatic-REVIEW_REPORT.md','SHA256SUMS.json':'original-automatic-SHA256SUMS.json'}.get(n,n);h=hashlib.sha256()
   with src.open(info) as i,out.open(new,'w',force_zip64=True) as o:
    while b:=i.read(1048576):h.update(b);o.write(b)
   hashes[new]=h.hexdigest()
   if n in previous:assert hashes[new]==previous[n],n
  for n,p in extras.items():
   assert n not in hashes;out.write(p,n);hashes[n]=sha(p)
  out.writestr('SHA256SUMS.json',json.dumps(hashes,indent=2)+'\n')
 with zipfile.ZipFile(dest) as z:
  assert set(z.namelist())==set(hashes)|{'SHA256SUMS.json'}
  for n,h in hashes.items():
   with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,n
 receipt={'archive':str(dest.relative_to(R)),'sha256':sha(dest),'size_bytes':dest.stat().st_size,'verified_payload_files':len(hashes),'time':time.time(),'original_archive_unchanged':sha(old)==original,'scope':'Offline terminal evidence correction; first valid SCF plus second unconverged partial; no new scientific run'}
 (E/'portable-review-v2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');dest.with_suffix('.zip.sha256').write_text(receipt['sha256']+'  '+dest.name+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
