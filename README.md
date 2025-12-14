# NLP Benchmark Platform

A comprehensive, production-grade platform for benchmarking **OpenAI models vs Amazon Bedrock models** across multiple NLP tasks with a modern web UI.

## Features

- **Multi-Provider Support**: Compare OpenAI (GPT-4, GPT-3.5) and Amazon Bedrock (Claude 3) models
- **Built-in NLP Tasks**: Classification, NER, Summarization, QA, Similarity, NLI, Translation
- **Custom Task Upload**: Add your own datasets and task definitions via ZIP upload
- **Modern Web UI**: Interactive dashboard for configuring runs, monitoring progress, and visualizing results
- **Async Job Queue**: Celery-based background processing for long-running benchmarks
- **Comprehensive Metrics**: Accuracy, F1, ROUGE, BLEU, exact match, and more
- **Performance Analytics**: Latency (p50/p95/p99) and cost estimation tracking
- **Result Visualization**: Charts and tables with data export to CSV

## Architecture

```
nlp-benchmark-platform/
├── backend/              # FastAPI application
│   ├── api/             # API routes
│   ├── providers/       # Model provider clients (OpenAI, Bedrock)
│   ├── metrics/         # Metrics calculation
│   ├── tasks/           # Task definitions and loaders
│   └── celery_app.py    # Celery worker configuration
├── frontend/            # React + TypeScript UI
│   └── src/
│       ├── pages/       # UI pages
│       ├── api.ts       # API client
│       └── types.ts     # TypeScript types
└── docker-compose.yml   # Docker orchestration
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional, for OpenAI models)
- AWS credentials (optional, for Bedrock models)

### 1. Clone and Configure

```bash
git clone <repository-url>
cd nlp-benchmark-platform

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 2. Start the Platform

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

The platform will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Run Your First Benchmark

1. Open http://localhost:3000
2. Click "New Run"
3. Select models and tasks to compare
4. Configure run parameters (temperature, max tokens, etc.)
5. Click "Create Run"
6. Monitor progress and view results

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | No | - |
| `AWS_ACCESS_KEY_ID` | AWS access key | No | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | No | - |
| `AWS_REGION` | AWS region | No | `us-east-1` |
| `DATABASE_URL` | Database connection string | No | `sqlite:///./storage/benchmark.db` |
| `REDIS_URL` | Redis connection string | No | `redis://localhost:6379/0` |

## Built-in Tasks

The platform includes these pre-configured tasks:

| Task | Type | Dataset | Metrics |
|------|------|---------|---------|
| SST-2 | Classification | Stanford Sentiment Treebank | Accuracy, F1 |
| AG News | Classification | AG News | Accuracy, F1 |
| CoNLL-2003 | NER | CoNLL-2003 | NER F1, Precision, Recall |
| XSum | Summarization | XSum | ROUGE-1, ROUGE-2, ROUGE-L |
| SQuAD v2 | QA | SQuAD v2 | Exact Match, F1 |
| STS-B | Similarity | STS Benchmark | Pearson, Spearman |
| MNLI | NLI | Multi-NLI | Accuracy, F1 |
| OPUS Books | Translation | OPUS Books (en-fr) | BLEU, ChrF |

## Adding Custom Tasks

### Task Definition Format

Create a ZIP file with the following structure:

```
my_custom_task.zip
├── task.yaml          # Task definition
├── test.jsonl         # Test dataset
├── validation.jsonl   # Validation dataset (optional)
└── README.md          # Documentation (optional)
```

### task.yaml Example

```yaml
task_id: sentiment_analysis
name: Product Review Sentiment
description: Binary sentiment classification for product reviews
task_type: classification

# Fields to use from dataset
input_fields:
  - review_text

# Field containing the ground truth label
label_field: sentiment

# Metrics to calculate
metrics:
  - accuracy
  - f1_macro

# Jinja2 template for model prompt
prompt_template: |
  Classify the sentiment of this product review as either 'positive' or 'negative'.

  Review: {{ review_text }}

  Sentiment:

# Dataset files for each split
splits:
  test: test.jsonl
  validation: validation.jsonl

# Optional: mapping from numeric labels to strings
golden_format:
  0: negative
  1: positive
```

### Dataset Format (JSONL)

```jsonl
{"review_text": "Great product, highly recommend!", "sentiment": 1}
{"review_text": "Poor quality, waste of money.", "sentiment": 0}
```

### Uploading

1. Navigate to "Upload Task" in the UI
2. Drop your ZIP file or click to browse
3. The system will validate and register your task
4. Use the "Test Task" feature to verify with 5 samples
5. Your task is now available in "New Run"

## API Reference

### Models

```http
GET /api/models
GET /api/models/credentials
```

### Tasks

```http
GET /api/tasks
GET /api/tasks/{task_id}
POST /api/tasks/upload
POST /api/tasks/{task_id}/test
```

### Runs

```http
POST /api/runs
GET /api/runs
GET /api/runs/{run_id}
GET /api/runs/{run_id}/results
GET /api/runs/{run_id}/leaderboard
GET /api/runs/{run_id}/logs
DELETE /api/runs/{run_id}
GET /api/exports/{run_id}.csv
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run API server
python main.py

# Run Celery worker
celery -A celery_app worker --loglevel=info
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Configuration

### Run Configuration Options

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `temperature` | Sampling temperature | 0.0 | 0.0 - 2.0 |
| `max_tokens` | Maximum tokens to generate | 512 | 1 - 4096 |
| `top_p` | Nucleus sampling | 1.0 | 0.0 - 1.0 |
| `timeout` | Request timeout (seconds) | 60 | 1 - 600 |
| `sample_cap` | Maximum samples to evaluate | None | 1+ |
| `trials` | Number of trials per sample | 1 | 1 - 10 |
| `split` | Dataset split to use | test | train/validation/test |

### Model Pricing

Cost estimates are based on token usage and configurable pricing in `backend/config.py`:

```python
MODEL_PRICING = {
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    # Add custom pricing as needed
}
```

## Supported Task Types

| Task Type | Description | Output Format | Example Metrics |
|-----------|-------------|---------------|-----------------|
| `classification` | Single-label classification | String label | accuracy, f1_macro |
| `multilabel` | Multi-label classification | List of labels | f1_micro, f1_macro |
| `ner` | Named entity recognition | List of entities | ner_f1, precision, recall |
| `summarization` | Text summarization | Summary text | rouge1, rouge2, rougeL |
| `qa` | Question answering | Answer text | exact_match, f1_qa |
| `similarity` | Semantic similarity | Float score (0-5) | pearson, spearman |
| `nli` | Natural language inference | Entailment label | accuracy, f1_macro |
| `translation` | Machine translation | Translated text | bleu, chrf |
| `freeform` | Free-form generation | Generated text | rougeL |

## Troubleshooting

### Backend not starting

```bash
# Check logs
docker compose logs backend

# Verify environment variables
docker compose exec backend env | grep -E 'OPENAI|AWS'

# Restart services
docker compose restart backend worker
```

### Worker not processing jobs

```bash
# Check worker logs
docker compose logs worker

# Verify Redis connection
docker compose exec backend redis-cli -h redis ping

# Restart worker
docker compose restart worker
```

### Frontend not connecting to backend

```bash
# Check backend health
curl http://localhost:8000/health

# Verify CORS settings in backend/config.py
# Rebuild frontend
docker compose up -d --build frontend
```

## Security Considerations

- **API Keys**: Never commit API keys to version control. Use `.env` file (gitignored)
- **File Uploads**: Max size enforced (100MB default), ZIP slip protection enabled
- **Input Validation**: All user inputs validated with Pydantic schemas
- **Rate Limiting**: Consider adding rate limiting for production deployments

## Performance Tips

- Use `sample_cap` to limit dataset size during testing
- Adjust `timeout` based on model and task complexity
- Use `temperature=0` for deterministic outputs
- Enable `trials > 1` only when measuring variance is important
- Monitor token usage to control costs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review API documentation at `/docs`
