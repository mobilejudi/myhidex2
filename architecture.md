# Architecture Schema

This diagram shows the logical architecture of the project.

## Global Architecture (Real-time)

[User/Clients]

- Web App (React/Next.js)
- Bot Telegram/Discord
- Trader (Phantom/Solflare)

    | WebSocket + REST
    v

[API Gateway (FastAPI)]

- Endpoints REST (signals, tokens, trade/prepare, trade/submit)
- WebSocket broadcast /ws
- Middleware Observability (Prometheus /metrics, /ops/readiness)
- Rate limiting, Correlation-ID
|                         ^
| publish/consume         | subscribe
v                         |
[Redis Streams (bus)]
- events.raw
- signals.out
- smart.activity
|                             ^
|                             |
v                             |
[Workers Ingestion] -------------------
- WS Supervisor (Helius, Triton) with failover
- Subscriptions logs: Pump.fun, Raydium (CP/CLMM), Token Program
- Enrichissement getTransaction (Helius Enhanced)
- Idempotence (signature), parsing, publication events.raw

    |
    v

[Moteur de Signaux]

- Agrégateur fenêtres 1m/5m (smart buys, netflow)
- Risk engine: authorities (mint/freeze), top holders, honeypot (Jupiter)
- Quote/impact (Jupiter)
- Scoring Strength 0–3
- Écrit DB (signals) + publie signals.out

    |                                     ^
    v                                     |

[Base de Données]                             |

- PostgreSQL + TimescaleDB (tokens, ticks, signals, trades, wallets)
- Requêtes API (list_signals, timeseries)    |

    |                                     |
    v                                     |

[Bot(s)] <--- consomme signals.out -----------

        |
        v
    [Pont de Trade Non‑Custodial]

- POST /trade/prepare-buy → récupère route Jupiter + tx non signée
- Client signe via Phantom/Solflare
- POST /trade/submit → sendRawTransaction (RPC)

    |
    v

[Providers externes]

- RPC/WS: Helius (+ Triton en backup)
- Jupiter Quote/Swap API
- Oracles (Pyth/Switchboard, optionnel)
- Indexeur holders (Flipside/Helius, optionnel)

## Security & Ops

- Secrets: Vault/KMS (clé Fernet), variables .env
- Logs structurés (structlog), audits WORM
- Policies de trading (limites per-trade/journalières, circuit breakers)
- CI/CD GitHub Actions, Docker/Compose/K8s
- Healthchecks: /ops/readiness, /metrics

## Main Flow

1) WS Ingestor receives logs (Pump.fun/Raydium) → enriches → events.raw
2) Signals Engine aggregates + calculates risks/score → DB + signals.out
3) API broadcasts in real-time on /ws and serves REST
4) Bot/Frontend receives the signal card; user buys
5) API prepare-buy (Jupiter) → wallet signs → submit → on-chain

## Data Tiers

- Hot: Redis Streams (real-time micro-batches)
- Warm: TimescaleDB (time-series, backtests)
- Cold (optional): S3/MinIO Parquet (archives, extended ML/backtest)

This diagram reflects the modules delivered in the code: connectors (WS/Helius), signals (aggregator/rules/engine), trading (jupiter/policy), api (REST/WS/metrics), bus (Redis), storage (SQLAlchemy), ops (logging, flags, scheduler), bots.
