"""Package reviewed converged frozen-water pair; preserve original archive."""
from pathlib import Path
import hashlib,json,zipfile,time
R=Path(__file__).resolve().parents[1];E=R/'evidence/qe75-second-v7'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 old=R/'artifacts/phase3/uio66_qe_water_pair_v7_windows.zip';dest=old.with_name('uio66_qe_water_pair_v7_windows_v2.zip')
 original='202bf5339a7d14cef5dc292c103704e759aba488731ec457a1b1957dfd5f51f6';assert sha(old)==original
 extras={}
 for n in ['independent-audit-v2.json','independent-audit-v1-failure.json','independent-force-crosscheck.csv','independent-resource-summary.json','postflight-followup.json','portable-review-receipt.json','finalization-complete.json']:extras['evidence/'+n]=E/n
 for n in ['audit_qe75_second_v7.py','audit_qe75_second_v7_v2.py','package_qe75_pair_v7_reviewed.py']:extras['controller/'+n]=R/'scripts'/n
 extras['REVIEW_REPORT.md']=R/'docs/UIO66_QE75_WATER_PAIR_V7_RESULTS.md';extras['updated-execution-config.json']=R/'configs/qe75-second-v7.json'
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
 receipt={'archive':str(dest.relative_to(R)),'sha256':sha(dest),'size_bytes':dest.stat().st_size,'verified_payload_files':len(hashes),'time':time.time(),'allocation_elapsed':time.time()-json.loads((E/'allocation.json').read_text())['allocation_start_unix'],'original_archive_unchanged':sha(old)==original,'scope':'Independent review of two converged frozen baseline SCFs; comparison provisional pending cutoff/grid; no new scientific run'}
 (E/'portable-review-v2-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');dest.with_suffix('.zip.sha256').write_text(receipt['sha256']+'  '+dest.name+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
