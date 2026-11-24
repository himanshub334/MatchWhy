import math
def precision_at_k(relevant,retrieved,k):
    return sum(1 for x in retrieved[:k] if x in set(relevant))/k if k else 0
def ndcg_at_k(relevant,retrieved,k):
    rel=set(relevant);dcg=sum(1/math.log2(i+2) for i,x in enumerate(retrieved[:k]) if x in rel)
    ideal=sum(1/math.log2(i+2) for i in range(min(k,len(rel))))
    return dcg/ideal if ideal else 0.0
