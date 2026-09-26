<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 01 - Deployment Options

## What this shows

Four realistic ways to run an ADK agent on Google Cloud. They trade how much
infrastructure you operate against how much control you keep. There is no best option,
only the one that fits your requirements; the questions below are the ones that change
the answer.

| Option | Fits when | Trade-off | Time to a first URL |
|---|---|---|---|
| Agent Runtime (managed) | You want managed sessions and memory, and no container work | Less control of the image; Agent Platform API instead of your own endpoint | minutes |
| Cloud Run | You want a container you control, scale to zero, and your own HTTPS endpoint | You own the image and its settings | minutes |
| GKE | You need sidecars, custom networking, or you already run a platform on GKE | Cluster operations and Kubernetes knowledge | hours |
| Self-hosted (VM, on-prem) | Compliance or data residency rules out managed services | You patch and operate everything | days |

## Prerequisites

None beyond the repository setup ([SETUP.md](../../SETUP.md)). Nothing is deployed in this topic.

## Run it

Nothing to run; this is a reference page. Topics 02, 03, and 08 deploy the options it
compares.

## What to look for

The questions in "How to choose" that change the answer for your workload: runtime
packages or sidecars, managed sessions, and who operates the platform.

## How to choose

```
Do you need system packages or sidecars in the runtime (Node.js for stdio MCP
servers, headless Chrome, a proxy container)?
  no:  do you want managed sessions/memory and no container to maintain?
         yes -> Agent Runtime   (adk deploy agent_engine, topic 02)
         no  -> Cloud Run       (adk deploy cloud_run, topic 03)
  yes: is one container per instance enough?
         yes -> Cloud Run with a custom Dockerfile (topic 08)
         no  -> do you already run GKE with a team that operates it?
                  yes -> GKE    (adk deploy gke)
                  no  -> Cloud Run first; move to GKE when you hit a concrete limit

Compliance forbids managed services? -> self-host on VMs or on-prem.
```

## Why Cloud Run is the usual starting point

For most single-agent services Cloud Run is the smallest thing that works: a container
(so you can install what you need), pay per request with scale to zero, IAM in front of
it, and nothing to patch. It stops fitting when you need multi-container pods, GPUs in
the same service, or long-lived connections beyond its request timeout.

Pick Agent Runtime when managed sessions and Memory Bank are worth more to you than
control of the image, for example an internal agent that other Agent Platform services
call.

Pick GKE when you already operate a cluster and need what Cloud Run does not offer:
sidecars, custom ingress, node-level controls, or bin-packing many services at sustained
high load.

## The expensive mistake

Choosing the target before anything has shipped. A team that builds a GKE platform "for
later" spends weeks on charts and networking before the first user sees the agent. Ship
on the simplest target that meets today's requirements, measure, and move when a
specific requirement forces it. `adk deploy` supports `agent_engine`, `cloud_run`, `gke`,
and `docker`, and the agent code is the same for all of them, so moving later is cheap.

## Further reading

- `../02_agent_runtime/` - the managed option.
- `../03_adk_deploy_cloud_run/` - one-command Cloud Run.
- `../08_custom_dockerfile/` - Cloud Run with your own image.
- ADK docs: Deploy (Agent Runtime, Cloud Run, GKE).
