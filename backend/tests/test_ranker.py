from types import SimpleNamespace
from app.ranker import rank_one,diversify
def test_hard_excluded_term_zeroes_constraint():
 j=SimpleNamespace(title="Engineering Manager",description="Manage a team",scope="Direct reports",skills=[],location="India",level="senior",retrieval_score=.9,posted_days_ago=1,company="A")
 p=SimpleNamespace(wants=["backend"],skills=[],excluded_terms=["manage a team"],preferred_locations=[],target_levels=[],minimum_retrieval_score=0)
 score,parts=rank_one(j,p)
 assert parts["constraint"]==0
def test_metrics_are_bounded():
 j=SimpleNamespace(title="Backend Engineer",description="Python backend",scope="Own services",skills=["python"],location="Remote India",level="mid",retrieval_score=.9,posted_days_ago=1,company="A")
 p=SimpleNamespace(wants=["python backend"],skills=["python"],excluded_terms=[],preferred_locations=[],target_levels=["mid"],minimum_retrieval_score=0)
 score,parts=rank_one(j,p)
 assert 0<=score<=1
