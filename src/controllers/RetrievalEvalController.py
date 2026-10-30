from math import log2

from controllers import NLPController, CatalogController


class RetrievalEvalController:
    def __init__(self, nlp_controller: NLPController):
        self.nlp_controller = nlp_controller

    @staticmethod
    def calculate_metrics(retrieved_ids: list[int], relevant_ids: list[int], k: int):
        """Binary relevance; precision uses K and reciprocal rank is cut off at K."""
        relevant = set(relevant_ids)
        remaining = relevant.copy()
        hits = 0
        reciprocal_rank = 0.0
        dcg = 0.0

        for rank, chunk_id in enumerate(retrieved_ids[:k], start=1):
            if chunk_id in remaining:
                remaining.remove(chunk_id)
                hits += 1
                dcg += 1 / log2(rank + 1)
                if reciprocal_rank == 0:
                    reciprocal_rank = 1 / rank

        ideal_dcg = sum(1 / log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
        return {
            "hit_rate_at_k": float(hits > 0),
            "recall_at_k": hits / len(relevant) if relevant else 0.0,
            "precision_at_k": hits / k,
            "mrr": reciprocal_rank,
            "ndcg_at_k": dcg / ideal_dcg if ideal_dcg else 0.0,
        }

    async def evaluate(self, project, samples: list[dict], k: int = 5):
        results = []
        for sample in samples:
            documents = await self.nlp_controller.search_vectordb_collection(
                project=project, text=sample["question"], limit=k
            )
            retrieved_ids = [document.chunk_id for document in (documents or [])][:k]
            metrics = self.calculate_metrics(retrieved_ids, sample["relevant_chunk_ids"], k)
            results.append({
                "question": sample["question"],
                "retrieved_chunk_ids": retrieved_ids,
                "metrics": metrics,
            })

        averages = {
            name: sum(result["metrics"][name] for result in results) / len(results)
            for name in results[0]["metrics"]
        }
        return {"k": k, "query_count": len(results), "metrics": averages, "results": results}




class ProductRetrievalEvalController:
    def __init__(self, catalog_controller: CatalogController):
        self.catalog_controller = catalog_controller



    # claculate metrics for hybrid product search
    @staticmethod
    def calculate_metrics(retrieved_ids: list[int], relevant_ids: list[int], k: int):
            """Binary relevance; precision uses K and reciprocal rank is cut off at K."""
            relevant = set(relevant_ids)
            remaining = relevant.copy()
            hits = 0
            reciprocal_rank = 0.0
            dcg = 0.0
    
            for rank, chunk_id in enumerate(retrieved_ids[:k], start=1):
                if chunk_id in remaining:
                    remaining.remove(chunk_id)
                    hits += 1
                    dcg += 1 / log2(rank + 1)
                    if reciprocal_rank == 0:
                        reciprocal_rank = 1 / rank
    
            ideal_dcg = sum(1 / log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
            return {
                "hit_rate_at_k": float(hits > 0),
                "recall_at_k": hits / len(relevant) if relevant else 0.0,
                "precision_at_k": hits / k,
                "mrr": reciprocal_rank,
                "ndcg_at_k": dcg / ideal_dcg if ideal_dcg else 0.0,
            }
    
    async def evaluate(self, samples: list[dict], k: int = 5):
            results = []
            for sample in samples:
                documents = await self.catalog_controller.hybrid_search(
                    query=sample["question"], limit=k, **sample["filters"]
                )
                retrieved_ids = [document.product_id for document in (documents or [])][:k]
                metrics = self.calculate_metrics(retrieved_ids, sample["relevant_chunk_ids"], k)
                results.append({
                    "question": sample["question"],
                    "retrieved_chunk_ids": retrieved_ids,
                    "metrics": metrics,
                })
    
            averages = {
                name: sum(result["metrics"][name] for result in results) / len(results)
                for name in results[0]["metrics"]
            }
            return {"k": k, "query_count": len(results), "metrics": averages, "results": results}
    