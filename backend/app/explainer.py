import httpx
from .config import settings
def explain(job,profile,breakdown):
    # Reason uses only facts present in profile/job. No unsupported claims are added.
    matched=[s for s in (job.skills or []) if s.lower() in {x.lower() for x in (profile.skills or [])}]
    want=" ".join(profile.wants or [])
    if settings.openai_api_key:
        prompt=("Write exactly one concise sentence explaining this job match. Use only facts below; "
                "do not invent benefits, requirements, seniority or company facts. If evidence is weak, say so.\n"
                f"PERSON WANTS: {want}\nPERSON SKILLS: {profile.skills}\nJOB: {job.title} at {job.company}\n"
                f"POSTING: {job.description}\nSCOPE: {job.scope}\nMATCHED SKILLS: {matched}\nSCORES: {breakdown}")
        try:
            r=httpx.post(settings.openai_base_url.rstrip("/")+"/chat/completions",
              headers={"Authorization":f"Bearer {settings.openai_api_key}"},
              json={"model":settings.llm_model,"temperature":0,"messages":[{"role":"user","content":prompt}]},timeout=25)
            r.raise_for_status()
            text=r.json()["choices"][0]["message"]["content"].strip().replace("\n"," ")
            return text[:350]
        except Exception: pass
    if matched:
        return f"This {job.level}-level {job.title} matches your interest in {want or 'this type of work'} and uses your {', '.join(matched[:3])} skills; the posting describes {job.scope[:115].rstrip('.')}."
    return f"This {job.title} is relevant to your stated interest in {want or 'the role'}; the posting describes {job.scope[:150].rstrip('.')}."
