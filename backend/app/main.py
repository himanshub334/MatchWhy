from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select,desc
from .db import Base,engine,get_db,Session as DBSession
from .models import Profile,CandidateJob,Recommendation,Feedback,EvaluationRun
from .schemas import ProfileIn,FeedbackIn
from .source import fetch_candidates
from .ranker import rank_one,diversify
from .explainer import explain
from .evaluator import evaluate
from .judge import judge_reason
app=FastAPI(title="MatchWhy API",version="1.0.0")
@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    db=DBSession()
    try:
        if not db.scalar(select(Profile)):
            db.add(Profile(name="Demo candidate",wants=["backend engineering","ownership","building reliable services","no people management"],skills=["python","postgresql","redis"],preferred_locations=["India","Remote"],target_levels=["mid","senior"],excluded_terms=["direct people management"],minimum_retrieval_score=0.0))
        if not db.scalar(select(CandidateJob)):
            for x in fetch_candidates():db.add(CandidateJob(**x))
        db.commit()
    finally:db.close()
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/api/profile")
def get_profile(db:Session=Depends(get_db)):
    p=db.scalar(select(Profile));return {k:getattr(p,k) for k in ["id","name","wants","skills","preferred_locations","target_levels","excluded_terms","minimum_retrieval_score"]}
@app.put("/api/profile")
def put_profile(payload:ProfileIn,db:Session=Depends(get_db)):
    p=db.scalar(select(Profile))
    for k,v in payload.model_dump().items():setattr(p,k,v)
    db.commit();return {"status":"saved"}
@app.post("/api/recommendations/refresh")
def refresh(db:Session=Depends(get_db)):
    profile=db.scalar(select(Profile)); candidates=db.scalars(select(CandidateJob).where(CandidateJob.active.is_(True))).all()
    ranked=[]
    for job in candidates:
        score,breakdown=rank_one(job,profile)
        if breakdown["constraint"]>0:ranked.append((job,score,breakdown))
    ranked.sort(key=lambda x:x[1],reverse=True)
    selected=diversify(ranked,limit=5)
    db.query(Recommendation).delete()
    out=[]
    for rank,(job,score,breakdown) in enumerate(selected,1):
        reason=explain(job,profile,breakdown)
        rec=Recommendation(job_id=job.id,rank=rank,total_score=score,score_breakdown=breakdown,reason=reason)
        db.add(rec);db.flush()
        out.append({"id":rec.id,"rank":rank,"job_id":job.id,"title":job.title,"company":job.company,"location":job.location,"level":job.level,"skills":job.skills,"url":job.url,"reason":reason,"score":score,"breakdown":breakdown,"judge":judge_reason(job,profile,reason)})
    db.commit();return {"count":len(out),"recommendations":out}
@app.get("/api/recommendations")
def recommendations(db:Session=Depends(get_db)):
    rows=db.scalars(select(Recommendation).order_by(Recommendation.rank)).all()
    out=[]
    for r in rows:
        j=db.get(CandidateJob,r.job_id)
        if j:out.append({"id":r.id,"rank":r.rank,"job_id":j.id,"title":j.title,"company":j.company,"location":j.location,"level":j.level,"skills":j.skills,"url":j.url,"reason":r.reason,"score":r.total_score,"breakdown":r.score_breakdown})
    return out
@app.post("/api/feedback")
def feedback(payload:FeedbackIn,db:Session=Depends(get_db)):
    if payload.kind not in ["good","wrong_job","weak_reason"]:raise HTTPException(400,"kind must be good, wrong_job, or weak_reason")
    if not db.get(Recommendation,payload.recommendation_id):raise HTTPException(404,"recommendation not found")
    db.add(Feedback(recommendation_id=payload.recommendation_id,kind=payload.kind,cause=payload.cause,note=payload.note));db.commit()
    return {"status":"recorded"}
@app.get("/api/quality")
def quality(db:Session=Depends(get_db)):
    rows=db.scalars(select(Feedback).order_by(desc(Feedback.created_at))).all()
    causes={}
    for r in rows:causes[r.cause]=causes.get(r.cause,0)+1
    fixes=[]
    mapping={"wrong_level":"Tighten level compatibility and add more labelled level pairs.","ignored_constraint":"Move this requirement into a hard filter and add a regression case.","generic_reason":"Require a concrete posting phrase and matched preference in every explanation.","other":"Review feedback notes and label the underlying failure mode."}
    for cause,count in sorted(causes.items(),key=lambda x:x[1],reverse=True):fixes.append({"cause":cause,"count":count,"suggested_fix":mapping.get(cause,mapping["other"])})
    return {"total_feedback":len(rows),"by_kind":{k:sum(1 for x in rows if x.kind==k) for k in ["good","wrong_job","weak_reason"]},"by_cause":causes,"weekly_fixes":fixes,"recent":[{"kind":r.kind,"cause":r.cause,"note":r.note} for r in rows[:12]]}
@app.post("/api/evaluation/run")
def run_eval(db:Session=Depends(get_db)):
    result=evaluate(db)
    # LLM judge summary on generated explanations; averages are reported separately from retrieval labels.
    profile=db.scalar(select(Profile)); recs=db.scalars(select(Recommendation).order_by(Recommendation.rank)).all()
    scores=[]
    for r in recs:
        job=db.get(CandidateJob,r.job_id);scores.append(judge_reason(job,profile,r.reason))
    def avg(k):return round(sum(float(x.get(k,0)) for x in scores)/len(scores),3) if scores else 0
    judge={"truthfulness":avg("truthfulness"),"specificity":avg("specificity"),"preference_alignment":avg("preference_alignment")}
    run=EvaluationRun(precision_at_5=result["precision_at_5"],ndcg_at_5=result["ndcg_at_5"],judge_truth=judge["truthfulness"],judge_specificity=judge["specificity"],judge_alignment=judge["preference_alignment"],passed=result["passed"],details=result["details"])
    db.add(run);db.commit()
    return {**result,"judge":judge,"run_id":run.id}
