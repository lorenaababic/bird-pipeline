# Bird Pipeline

An automated data pipeline that collects bird observation data, classifies bird sounds from audio recordings and generates a report with charts. Every step reads from and writes to cloud services, and the whole pipeline can be triggered from GitHub Actions.

<!-- Add a screenshot of the generated chart here:
![Report](docs/bird_report.png)
-->

## Pipeline steps

The workflow is orchestrated with **Snakemake** and runs in this order:

1. **Scrape species** — collects bird species data from the web and stores it in MongoDB.
2. **Consume Kafka** — reads bird observation events from a Kafka topic, normalises them and saves them to MongoDB.
3. **Process audio** — uploads audio recordings to S3-compatible object storage and sends them to a classification API to identify the species.
4. **Generate report** — aggregates the data into a CSV report, with optional fuzzy filtering by species name.
5. **Visualise** — creates a chart from the report.

## Tech stack

| Area | Technologies |
|------|--------------|
| Language | Python 3.11 |
| Orchestration | Snakemake |
| Messaging | Kafka (Upstash) |
| Database | MongoDB (MongoDB Atlas) |
| Object storage | MinIO / S3 API (Cloudflare R2) |
| CI / automation | GitHub Actions |
| Libraries | pandas, matplotlib, boto3, pymongo, confluent-kafka, rapidfuzz, BeautifulSoup |

## Running it

**With GitHub Actions**

Go to *Actions → Run Bird Pipeline → Run workflow*. You can optionally set a species filter (e.g. `Kingfisher`) and a fuzzy matching threshold. The CSV report is uploaded as a workflow artifact.

All credentials are stored as GitHub repository secrets, never in the code.

**Locally**
```bash
pip install -r requirements.txt
cp .env.example .env      # fill in your MongoDB, S3 and Kafka details
snakemake --cores 1
```

Optional parameters:
```bash
snakemake --cores 1 --config species_filter="Kingfisher" fuzzy_threshold=80
```

## Project structure

```
├── Snakefile                  # pipeline definition
├── scripts/                   # one script per pipeline step
├── utils/                     # MongoDB, S3 and Kafka clients
├── config/config.py           # configuration from environment variables
└── .github/workflows/         # GitHub Actions workflow
```
