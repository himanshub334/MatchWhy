from datetime import datetime,timezone
from sqlalchemy import String,Text,DateTime,Float,JSON,Boolean,ForeignKey,Integer
from sqlalchemy.orm import Mapped,mapped_column
from .db import Base
def now(): return datetime.now(timezone.utc)
class Profile(Base):
    __tablename__="profiles"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120),default="Demo candidate")
    wants:Mapped[list]=mapped_column(JSON,default=list)
    skills:Mapped[list]=mapped_column(JSON,default=list)
    preferred_locations:Mapped[list]=mapped_column(JSON,default=list)
    target_levels:Mapped[list]=mapped_column(JSON,default=list)
    excluded_terms:Mapped[list]=mapped_column(JSON,default=list)
    minimum_retrieval_score:Mapped[float]=mapped_column(Float,default=0.0)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class CandidateJob(Base):
    __tablename__="candidate_jobs"
    id:Mapped[int]=mapped_column(primary_key=True)
    external_id:Mapped[str]=mapped_column(String(200),unique=True,index=True)
    title:Mapped[str]=mapped_column(String(300))
    company:Mapped[str]=mapped_column(String(200))
    location:Mapped[str]=mapped_column(String(200),default="Unknown")
    level:Mapped[str]=mapped_column(String(80),default="mid")
    skills:Mapped[list]=mapped_column(JSON,default=list)
    description:Mapped[str]=mapped_column(Text,default="")
    scope:Mapped[str]=mapped_column(Text,default="")
    url:Mapped[str]=mapped_column(Text,default="")
    retrieval_score:Mapped[float]=mapped_column(Float,default=0)
    posted_days_ago:Mapped[int]=mapped_column(Integer,default=7)
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Recommendation(Base):
    __tablename__="recommendations"
    id:Mapped[int]=mapped_column(primary_key=True)
    job_id:Mapped[int]=mapped_column(ForeignKey("candidate_jobs.id"))
    rank:Mapped[int]=mapped_column(Integer)
    total_score:Mapped[float]=mapped_column(Float)
    score_breakdown:Mapped[dict]=mapped_column(JSON,default=dict)
    reason:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Feedback(Base):
    __tablename__="feedback"
    id:Mapped[int]=mapped_column(primary_key=True)
    recommendation_id:Mapped[int]=mapped_column(ForeignKey("recommendations.id"))
    kind:Mapped[str]=mapped_column(String(30))
    cause:Mapped[str]=mapped_column(String(50),default="other")
    note:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class EvaluationRun(Base):
    __tablename__="evaluation_runs"
    id:Mapped[int]=mapped_column(primary_key=True)
    precision_at_5:Mapped[float]=mapped_column(Float)
    ndcg_at_5:Mapped[float]=mapped_column(Float)
    judge_truth:Mapped[float]=mapped_column(Float)
    judge_specificity:Mapped[float]=mapped_column(Float)
    judge_alignment:Mapped[float]=mapped_column(Float)
    passed:Mapped[bool]=mapped_column(Boolean)
    details:Mapped[dict]=mapped_column(JSON,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
