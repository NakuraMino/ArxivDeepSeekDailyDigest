# Arxiv DeepSeek Daily Digest

A Deepseek-powered agent designed to deliver daily email updates on newly uploaded papers to ArXiv that align with your specific research interests.

### System Requirements

You will need a GPU machine to run LLM inference. I use a 4090 GPU, but you can adjust the LLM type and parameters to fit your machine.

### Getting Started

Set up your conda environment by running
```
conda env create -f environment.yml
```

To install this repository to your current environment, run:

```
pip install -e .
```

Modify `configs/interests.yaml` to match your interests. Also modify `config/arxiv.yaml` to match the query parameters for arxiv.

I use `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` as my LLM for paper classification, but you can easily swap this out by checking the [list of supported models](https://docs.vllm.ai/en/latest/models/supported_models.html) and modifying `configs/llm.yaml`. You can also easily adjust `max_model_len` to fit your GPU size. To ensure the language model is saved to your preferred path, export the following environment variable.

```
export HF_HOME=/path/to/save/models
```

Set up your Google Developer Console and enable Gmail API use. I followed this [tutorial](https://mailtrap.io/blog/send-emails-with-gmail-api/). Then, modify `configs/email.yaml` to configure the email sender and receiver address. The email sender should be the same gmail account you used to enable the Gmail API. Download your google `credentials.json` and save to `configs/`.

To make sure your Google Developer Console is working correctly, you can run

```
cd src/daily_digest/
python google_quickstart.py
```

After confirming, delete your `configs/token.json`. You will generate a new one with more permissions when running the full service.

Now run below and confirm you received an email with a daily digest.

```
cd src/daily_digest/
python main.py
```

To add this as a cron job on your machine, you can `crontab -e` and add the following line:
```
0 7 * * 1-5 /path/to/ArxivDailyDigest/src/daily_digest/run.sh
```
This will run this script at 7am every weekday morning. Make sure to modify `run.sh` as appropriate. You also want to create a directory for your logs:

```
cd src/daily_digest/
mkdir logs/
```
