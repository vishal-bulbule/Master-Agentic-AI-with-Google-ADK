<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 10 - Autoscaling Settings for Agents

## What this shows

Cloud Run's defaults suit web endpoints that answer in well under a second. An agent
request is different: one `/run_sse` call can hold a connection for 5 to 30 seconds
while it waits on several model calls, and the Python process with ADK loaded uses a
few hundred MB before any request arrives. This page covers the settings that matter
for that shape of workload and how to tune them from real metrics.

## Prerequisites

- Mostly reading. To apply the settings you need the `greet-agent` service from
  `../03_adk_deploy_cloud_run/`, the gcloud CLI logged in, and `roles/run.developer`
  plus `roles/iam.serviceAccountUser` on the runtime service account (topic 03 and 05
  show the grant commands).
- To read the metrics: `roles/monitoring.viewer`, or `roles/run.viewer` for the Cloud Run
  Metrics tab.

## Run it

Apply the starting point below to the topic 03 service (creates a new revision):

1. `gcloud run services update greet-agent --region=us-central1 --min-instances=0 --max-instances=10 --concurrency=4 --cpu=2 --memory=2Gi`
2. Send a few requests (topic 09), then open the service's Metrics tab in the Cloud Run
   console.

## What to look for

Cloud Run console, your service, Metrics tab:

- Request count and latency (p50, p95, p99) for sizing.
- Container instance count: is scaling happening, and is it hitting `max-instances`?
- CPU and memory utilization: over- or under-provisioned?
- Container startup latency: your cold-start cost.

## The settings

| Flag | Cloud Run default | What it controls |
|---|---|---|
| `--min-instances` | 0 | Instances kept warm. 0 scales to zero (no idle cost, cold starts). |
| `--max-instances` | 100 | Upper bound on instances: your cost and quota ceiling. |
| `--concurrency` | 80 | Requests one instance serves at the same time. |
| `--cpu` | 1 | vCPUs per instance. |
| `--memory` | 512Mi | Memory per instance. |
| `--timeout` | 300s | Maximum request duration, up to 3600s. Long streaming sessions can hit it. |
| `--cpu-throttling` / `--no-cpu-throttling` | throttled | Whether CPU is available outside requests (needed for background work). |

With `adk deploy cloud_run`, pass them after `--`:

```bash
adk deploy cloud_run \
  --project="$GCP_PROJECT" --region=us-central1 --service_name=greet-agent \
  --env GOOGLE_CLOUD_LOCATION=global \
  ./greet_agent \
  -- --min-instances=0 --max-instances=10 --concurrency=4 --cpu=2 --memory=2Gi --timeout=300s
```

Or change a running service (creates a new revision):

```bash
gcloud run services update greet-agent --region=us-central1 \
  --min-instances=0 --max-instances=10 --concurrency=4 --cpu=2 --memory=2Gi
```

## A starting point, and why

| Setting | Value | Reasoning |
|---|---|---|
| `min-instances` | 0 | No idle cost. Accept cold starts until traffic or latency targets say otherwise. |
| `max-instances` | 10 | Caps spend and the rate of model calls if traffic spikes or a client loops. |
| `concurrency` | 4 | Each request mostly waits on the model, but event serialization and tool code still use CPU; 4 per 2 vCPU leaves headroom. |
| `cpu` | 2 | Keeps one slow request from starving the others on the same instance. |
| `memory` | 2Gi | ADK and its dependencies plus in-memory sessions and tracing buffers; 1Gi can run out under load. |

These are a first guess for this small agent, not a rule. An agent that mostly waits on
remote calls may run fine at concurrency 20 on 1 vCPU; an agent that parses large
documents in tools may need concurrency 1. Measure.

## Tuning from metrics

Ship with the starting point, watch a week of real traffic, then change one setting at
a time:

1. Cold starts hurt users: set `min-instances=1` on the service users call directly.
   You then pay for that instance while idle.
2. Instances restart with out-of-memory errors in the logs: raise `memory`. Lowering
   `concurrency` only hides a leak.
3. CPU near 100% with latency rising: raise `cpu`, or lower `concurrency`.
4. Latency rising at the same request rate with CPU and memory headroom: requests are
   queuing; raise `concurrency` or `max-instances`.
5. Unexpected cost: lower `max-instances` and find what drove the traffic.

Sizing check: at 8 requests per second, 5 seconds per request, and concurrency 4, you
need 8 x 5 / 4 = 10 instances at steady state. Set `max-instances` above that with some
margin.

## The cold-start trade-off

| `min-instances=0` | `min-instances=1` |
|---|---|
| First request after idle waits for a container start and ADK import (several seconds) | Warm instance answers immediately |
| No cost while idle | You pay for one instance around the clock |
| Development, demos, low-traffic internal tools | User-facing services with latency targets |

A common split: `min-instances=1` only for the production service in its main region,
0 everywhere else. `--cpu-boost` (on by default for new services) shortens cold starts
by giving extra CPU during startup.

## When these settings stop being enough

| Signal | Next step |
|---|---|
| `max-instances` reached regularly | Raise it after checking cost per request |
| GPU work inside the agent loop | Move that work to a separate model endpoint; keep the agent on Cloud Run |
| High sustained load across many services | Compare the cost with GKE, where you pack services onto shared nodes |

## Clean up

Settings only cost money through `--min-instances` above 0 or CPU always allocated. To
go back to the defaults:

```bash
gcloud run services update greet-agent --region=us-central1 \
  --min-instances=0 --max-instances=100 --concurrency=80 --cpu=1 --memory=512Mi
```
