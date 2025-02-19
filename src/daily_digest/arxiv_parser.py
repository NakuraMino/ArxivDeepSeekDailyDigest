import arxiv
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
from types import SimpleNamespace

@dataclass
class ArxivPaper:
    title: str
    authors: str
    summary: str
    published: str
    url: str

class ArxivParser:

    def __init__(self, preference_cfg):
        self.client = arxiv.Client()
        with open(preference_cfg, "r") as file:
           self.cfg = SimpleNamespace(**yaml.safe_load(file))

    def fetch_papers(self):
        papers = []
        for query in self.cfg.queries:
            papers.extend(self._fetch_papers_from_query(query))
        papers = list({p.title: p for p in papers}.values())
        return papers

    def _fetch_papers_from_query(self, search_query, max_results=400, attempts=5):
        if attempts <=0:
            raise arxiv.UnexpectedEmptyPageError("yeah its not happening")
        try:
            today = (datetime.today() - timedelta(days=1)) .strftime("%Y%m%d")
            query = f"{search_query}" #  AND submittedDate:[{today} TO {today}]"
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )        
            papers = []
            for result in self.client.results(search):
                if self.cfg.category not in result.categories:
                    continue
                if not result.published.strftime('%Y%m%d') == today:
                    continue 
                paper = ArxivPaper(
                    title = result.title, 
                    authors = ", ".join([author.name for author in result.authors]),
                    summary = result.summary,
                    published = result.published.strftime('%Y-%m-%d'),
                    url = result.entry_id
                )
                papers.append(paper)
            return papers
        except arxiv.UnexpectedEmptyPageError:
            return self._fetch_papers_from_query(search_query, max_results=max_results, attempts=attempts - 1)

if __name__ == '__main__':
    parser = ArxivParser("configs/arxiv.yaml")
    results = parser.fetch_papers()
    for r in results:
        print(r.published)
        print(r.title)