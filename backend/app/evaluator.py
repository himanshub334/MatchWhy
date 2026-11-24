import json
from pathlib import Path
from sqlalchemy import select
from .models import CandidateJob
from .ranker import rank_one,diversify
from .metrics import precision_at_k,ndcg_at_k
from .explainer import explain
def evaluate(db):
    base=Path(__file__).resolve().parents[1]/"eval"
    cases=json.loads((base/"labelled_pairs.json").read_text())
    profile=db.scalar(select(__import__("app.models",fromlist=["Profile"]).Profile))
    jobs=db.scalars(select(CandidateJob).where(CandidateJob.active.is_(True))).all()
    all_results=[];pvals=[];nvals=[]
    for case in cases:
        # Query-specific wants provide a consistent evaluation profile.
        class P: pass
        p=P();p.wants=[case["query"]];p.skills=[];p.excluded_terms=[];p.preferred_locations=[];p.target_levels=[];p.minimum_retrieval_score=0
        ranked=sorted([(j,*rank_one(j,p)) for j in jobs],key=lambda x:x[1],reverse=True)
        selected=diversify(ranked,per_company=1,limit=5)
        ids=[x[0].external_id for x in selected]
        pvals.append(precision_at_k(case["relevant_ids"],ids,5));nvals.append(ndcg_at_k(case["relevant_ids"],ids,5))
        all_results.append({"query":case["query"],"retrieved":ids,"precision_at_5":pvals[-1],"ndcg_at_5":nvals[-1]})
    precision=sum(pvals)/len(pvals) if pvals else 0;ndcg=sum(nvals)/len(nvals) if nvals else 0
    thresholds=json.loads((base/"thresholds.json").read_text())
    return {"precision_at_5":precision,"ndcg_at_5":ndcg,"passed":precision>=thresholds["minimum_precision_at_5"] and ndcg>=thresholds["minimum_ndcg_at_5"],"details":all_results}
