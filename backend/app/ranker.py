import re
from .models import CandidateJob
LEVEL={"intern":0,"junior":1,"entry":1,"mid":2,"senior":3,"staff":4,"lead":4,"principal":5}
def words(s): return set(re.findall(r"[a-z0-9+#.]+",(s or "").lower()))
def rank_one(job,profile):
    wants=" ".join(profile.wants or [])
    wanted=words(wants)|words(" ".join(profile.skills or []))
    job_words=words(" ".join([job.title,job.description,job.scope," ".join(job.skills or [])]))
    overlap=len(wanted & job_words)/max(1,len(wanted))
    constraint=1.0
    reasons=[]
    combined=(job.title+" "+job.description+" "+job.scope).lower()
    for term in profile.excluded_terms or []:
        if term.lower() in combined:
            constraint=0.0; reasons.append("excluded_term")
    if profile.preferred_locations and not any(x.lower() in job.location.lower() for x in profile.preferred_locations):
        constraint*=0.45; reasons.append("location_mismatch")
    if profile.target_levels:
        if job.level.lower() not in [x.lower() for x in profile.target_levels]:
            constraint*=0.55; reasons.append("wrong_level")
    if job.retrieval_score < profile.minimum_retrieval_score:
        constraint=0.0; reasons.append("retrieval_below_minimum")
    seniority=1.0
    target=" ".join(profile.target_levels or []).lower()
    if target and job.level.lower() not in target: seniority=0.55
    scope_score=0.85 if any(x in (job.scope+" "+job.description).lower() for x in ["own","end to end","ownership","technical direction"]) else 0.45
    freshness=max(0.15,1-(job.posted_days_ago/30))
    total=(0.30*job.retrieval_score+0.25*overlap+0.20*constraint+0.10*seniority+0.10*scope_score+0.05*freshness)
    return round(total,5),{"retrieval":round(job.retrieval_score,3),"preference_overlap":round(overlap,3),
      "constraint":round(constraint,3),"seniority":round(seniority,3),"scope":round(scope_score,3),
      "freshness":round(freshness,3),"flags":reasons}
def diversify(ranked,per_company=1,limit=5):
    out=[];companies=set();titles=set()
    for item in ranked:
        job=item[0]; title=re.sub(r"\b(senior|junior|staff|lead|principal)\b","",job.title.lower()).strip()
        if job.company.lower() in companies or title in titles: continue
        out.append(item);companies.add(job.company.lower());titles.add(title)
        if len(out)>=limit:break
    return out
