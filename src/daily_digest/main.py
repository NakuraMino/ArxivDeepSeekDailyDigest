from daily_digest.llm_judge import LLMJudge
from daily_digest.arxiv_parser import ArxivParser
from daily_digest.email_handler import GmailClient

def main():
    parser = ArxivParser("configs/arxiv.yaml")
    judge = LLMJudge()
    sender = GmailClient(email_cfg='configs/my_email.yaml')
    results = parser.fetch_papers()
    papers = judge.classify_papers(results)
    sender.send_email(papers)

if __name__ == "__main__":
    main()