from app.db import Base,engine,Session
from app.main import startup
from app.evaluator import evaluate
import json
startup()
db=Session()
try:
 result=evaluate(db);print(json.dumps(result,indent=2))
 if not result["passed"]:raise SystemExit(1)
finally:db.close()
