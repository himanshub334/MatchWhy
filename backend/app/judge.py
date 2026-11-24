import re
from .explainer import explain
from .config import settings
import httpx
def judge_reason(job,profile,reason):
    if settings.openai_api_key:
        prompt=("Score the recommendation reason from 1 to 5 on truthfulness, specificity, and preference_alignment. "
                "Only use the supplied job/profile evidence. Return JSON with those three numeric fields.\n"
                f"PROFILE:{profile.wants} {profile.skills}\nJOB:{job.title} {job.description} {job.scope}\nREASON:{reason}")
        try:
            r=httpx.post(settings.openai_base_url.rstrip("/")+"/chat/completions",headers={"Authorization":f"Bearer {settings.openai_api_key}"},
              json={"model":settings.llm_model,"temperature":0,"response_format":{"type":"json_object"},"messages":[{"role":"user","content":prompt}]},timeout=30)
            r.raise_for_status();return r.json()["choices"][0]["message"]["content"]
        except Exception: pass
    evidence=set(re.findall(r"[a-z0-9+#.]+",(job.title+" "+job.description+" "+job.scope).lower()))
    tokens=set(re.findall(r"[a-z0-9+#.]+",reason.lower()))
    overlap=len(evidence&tokens)/max(1,len(tokens))
    pref=set(re.findall(r"[a-z0-9+#.]+"," ".join(profile.wants or [])+" ".join(profile.skills or []).lower()))
    alignment=len(pref&tokens)/max(1,len(pref))
    return {"truthfulness":round(min(5,2+3*overlap),2),"specificity":round(min(5,1+4*overlap),2),"preference_alignment":round(min(5,1+4*alignment),2)}
