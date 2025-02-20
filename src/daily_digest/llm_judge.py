from vllm import LLM, SamplingParams
import yaml 
from types import SimpleNamespace


class LLMJudge:

    def __init__(self, config='configs/interests.yaml',
                 llm_config="configs/llm.yaml"):
        with open(config, "r") as file:
            self.cfg = SimpleNamespace(**yaml.safe_load(file))
            for i, paper in enumerate(self.cfg.papers):
                self.cfg.papers[i] = SimpleNamespace(**paper)
        with open(llm_config, "r") as file:
            self.llm_cfg = SimpleNamespace(**yaml.safe_load(file))          
            self.model = self.llm_cfg.llm
            self.llm = LLM(model=self.model, max_model_len=self.llm_cfg.max_model_len)
            self.sampling_params = SamplingParams(temperature=self.llm_cfg.temperature, 
                                                  top_p=self.llm_cfg.top_p,
                                                  max_tokens=self.llm_cfg.max_tokens)

    def classify_papers(self,results_list):
        query_format = \
        "**Task**: Determine whether the new paper is interesting based on a given list of relevant papers and keywords.\n\n" + \
        "**Instructions**: {instructions}\n" + \
        "**Keywords**: {keywords}\n\n" + \
        "**Relevant Papers**: {preferences}\n"

        instructions = (
            "1. Carefully analyze the provided keywords and the list of relevant papers to understand the core topics of interest.\n"
            "2. Evaluate the new paper against these references, considering relevance to two or more keywords or papers. "
            "It does not need to match all keywords but should have a meaningful connection to the research theme.\n"
            "3. Think critically and iterate through your reasoning at least three times before making a final decision. "
            "Reading papers is time-consuming, so only recommend truly relevant papers.\n\n"
            "4. Structure your response as follows:\n"
            "- Reasoning process enclosed within <think></think> tags.\n"
            "- Final explanation enclosed within <reason></reason> tags.\n"
            "- Final verdict (either <answer>yes</answer> or <answer>no</answer>).\n"
        )


        keywords = ", ".join([keyword for keyword in self.cfg.interests])
        authors = ", ".join([keyword for keyword in self.cfg.authors])
        preferences = "\n\n"
        for i, paper in enumerate(self.cfg.papers):
            title = f"Title: {paper.title}\n"
            authors = f"Authors: {paper.authors}\n"
            summary = f"Summary: {paper.summary}\n\n"
            preferences += title + authors + summary
        query = query_format.format(instructions=instructions, keywords=keywords, preferences=preferences, authors=authors)  + "**New Paper**: {paper}\n"
        prompts = []
        for i, result in enumerate(results_list):
            title = f"Title: {result.title}\n"
            authors = f"Authors: {result.authors}\n"
            summary = f"Summary: {result.summary}\n"
            paper = title + authors + summary
            prompts.append(query.format(paper=paper))
        outputs = self.llm.generate(prompts, self.sampling_params)
        good_papers = []
        for i,output in enumerate(outputs):
            response = output.outputs[0].text
            print(output.outputs[0].text)
            print("****END*****\n")
            if self._has_notable_author(results_list[i].authors):
                good_papers.append(results_list[i])
            elif "<answer>yes</answer>" in response:
                good_papers.append(results_list[i])
        return good_papers

    def _has_notable_author(self, author_list):
        return bool(set(author_list.split(', ')) & set(self.cfg.authors))

if __name__ == "__main__":
    from daily_digest.arxiv_parser import ArxivParser
    parser = ArxivParser("configs/arxiv.yaml")
    judge = LLMJudge()
    results = parser.fetch_papers("robot learning")
    good_papers = judge.classify_papers(results)
    for i, result in enumerate(good_papers):
        paragraph = "<p>"
        title = f"Title: {result.title}\n"
        authors = f"Authors: {result.authors}\n"
        summary = f"Summary: {result.summary}\n"
        url = f"URL: <a href='{result.url}'></a>\n"
        paragraph += title + authors + summary + url + "\n<p>"
        print(paragraph)