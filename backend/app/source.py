import httpx
from .config import settings
DEMO=[
 {"external_id":"js-101","title":"Backend Engineer","company":"Northstar","location":"Remote, India","level":"mid","skills":["python","fastapi","postgresql","redis"],"description":"Build Python APIs and reliable backend services. Work closely with product and own features end to end.","scope":"Individual contributor ownership of services; no direct reports.","url":"https://example.com/jobs/101","retrieval_score":0.92,"posted_days_ago":2},
 {"external_id":"js-102","title":"Senior Platform Engineer","company":"Orbit Cloud","location":"Bengaluru, India","level":"senior","skills":["python","aws","kubernetes","kafka"],"description":"Own distributed platform reliability and technical direction. Mentor engineers without formal people management.","scope":"Own platform roadmap and technical decisions; no direct reports.","url":"https://example.com/jobs/102","retrieval_score":0.89,"posted_days_ago":4},
 {"external_id":"js-103","title":"Engineering Manager","company":"BrightCart","location":"Hyderabad, India","level":"senior","skills":["python","aws"],"description":"Manage a team of eight engineers and conduct performance reviews.","scope":"Direct people management and delivery ownership.","url":"https://example.com/jobs/103","retrieval_score":0.95,"posted_days_ago":1},
 {"external_id":"js-104","title":"Full Stack Developer","company":"Cedar Labs","location":"Remote, India","level":"junior","skills":["react","typescript","python","postgresql"],"description":"Build user-facing product features and backend APIs with a small team.","scope":"Own feature delivery from implementation to production.","url":"https://example.com/jobs/104","retrieval_score":0.84,"posted_days_ago":3},
 {"external_id":"js-105","title":"Data Engineer","company":"Lakehouse Co","location":"Mumbai, India","level":"mid","skills":["python","sql","kafka","aws"],"description":"Build data pipelines and own data quality, observability and reliability.","scope":"Individual contributor ownership of data workflows.","url":"https://example.com/jobs/105","retrieval_score":0.81,"posted_days_ago":6},
 {"external_id":"js-106","title":"Java Backend Developer","company":"Pine Systems","location":"Pune, India","level":"mid","skills":["java","spring","postgresql","docker"],"description":"Develop Spring services and own API performance and reliability.","scope":"Own services and technical delivery; no people management.","url":"https://example.com/jobs/106","retrieval_score":0.78,"posted_days_ago":9}
]
def fetch_candidates():
    if settings.jobsense_api_url:
        try:
            r=httpx.get(settings.jobsense_api_url.rstrip("/")+"/api/jobs",timeout=8);r.raise_for_status()
            items=r.json()
            if items:
                return [{"external_id":str(x.get("source_id",x.get("id"))),"title":x["title"],"company":x.get("company","Unknown"),
                  "location":x.get("location","Unknown"),"level":x.get("level","mid"),"skills":x.get("skills",[]),
                  "description":x.get("description",""),"scope":x.get("responsibility_scope",""),
                  "url":x.get("url",""),"retrieval_score":0.7,"posted_days_ago":7} for x in items]
        except Exception: pass
    return DEMO
