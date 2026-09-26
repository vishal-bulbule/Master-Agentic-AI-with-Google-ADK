<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 11 - GitHub Actions CI/CD

## What this shows

A pipeline where every push to `main` runs the tests first and deploys only if they
pass. A failing eval is a failing build, and a failing build does not reach production.

`.github/workflows/deploy.yml`:

1. Checks out the repository and installs `requirements-dev.txt`.
2. Authenticates to Google Cloud with Workload Identity Federation (no stored key).
3. Runs `pytest tests`: unit tests of the tool, then a two-case eval against the real
   model. The eval uses Agent Platform (formerly Vertex AI) with the credentials from
   step 2, so CI needs no Gemini API key.
4. Runs `adk deploy cloud_run ... -- --no-allow-unauthenticated`.

```
11_github_actions_cicd/
|-- .github/workflows/deploy.yml   copy to .github/workflows/ at your repository root
|-- conftest.py                    sys.path and .env loading for pytest
|-- requirements-dev.txt           what CI installs
|-- greet_agent/                   the agent (requirements.txt is what the image installs)
`-- tests/
    |-- test_greet_tool.py         unit tests, no model calls
    |-- test_greet_eval.py         eval gate with AgentEvaluator
    |-- greet.test.json            two eval cases
    `-- test_config.json           trajectory 1.0, response match 0.8
```

## Prerequisites

Local test run:

- The repository setup ([SETUP.md](../../SETUP.md)), or `pip install -r requirements-dev.txt`
  (what CI installs).
- Credentials: copy `greet_agent/.env.example` to `greet_agent/.env` and fill it in
  (`conftest.py` loads it). Use the Agent Platform option (`GOOGLE_GENAI_USE_ENTERPRISE=TRUE`,
  `GOOGLE_CLOUD_LOCATION=global`) to match what CI does.

One-time Google Cloud setup for the pipeline (run as a project Owner, or with
`roles/iam.serviceAccountAdmin`, `roles/iam.workloadIdentityPoolAdmin`, and
`roles/resourcemanager.projectIamAdmin`):

1. Enable the APIs the pipeline and the auth exchange use:

   ```bash
   export GCP_PROJECT=your-project-id
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
     artifactregistry.googleapis.com aiplatform.googleapis.com \
     iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com \
     --project="$GCP_PROJECT"
   ```

2. Create the deployer service account and grant it what the pipeline does: source
   deploys to Cloud Run, acting as the service's runtime account, and model calls for
   the eval:

   ```bash
   PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
   gcloud iam service-accounts create deployer --display-name="GitHub Actions deployer" \
     --project="$GCP_PROJECT"
   DEPLOYER="deployer@${GCP_PROJECT}.iam.gserviceaccount.com"

   for ROLE in roles/run.sourceDeveloper roles/serviceusage.serviceUsageConsumer roles/aiplatform.user; do
     gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
       --member="serviceAccount:$DEPLOYER" --role="$ROLE"
   done

   # Deploying a service means acting as its runtime service account (the default compute one).
   gcloud iam service-accounts add-iam-policy-binding \
     "${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
     --member="serviceAccount:$DEPLOYER" --role="roles/iam.serviceAccountUser"
   ```

3. Give the build and runtime identity its roles: `roles/cloudbuild.builds.builder`
   (`../07_cloud_build_perms/`) and `roles/aiplatform.user` (see `../03_adk_deploy_cloud_run/`).
   Deploy once by hand with topic 03 so the `cloud-run-source-deploy` Artifact Registry
   repository exists.

4. Workload Identity Federation: let GitHub exchange its OIDC token for the deployer
   account, limited to your repository:

   ```bash
   REPO="<your-org>/<your-repo>"
   gcloud iam workload-identity-pools create gh-pool --location=global --project="$GCP_PROJECT"
   gcloud iam workload-identity-pools providers create-oidc gh-provider \
     --project="$GCP_PROJECT" \
     --location=global \
     --workload-identity-pool=gh-pool \
     --issuer-uri="https://token.actions.githubusercontent.com" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
     --attribute-condition="assertion.repository=='$REPO'"

   gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER" \
     --role=roles/iam.workloadIdentityUser \
     --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUM}/locations/global/workloadIdentityPools/gh-pool/attribute.repository/$REPO"
   ```

5. In the GitHub repository settings, under Secrets and variables, Actions, Variables,
   add:

   | Variable | Value |
   |---|---|
   | `GCP_PROJECT` | your project id |
   | `WIF_PROVIDER` | `projects/<number>/locations/global/workloadIdentityPools/gh-pool/providers/gh-provider` |
   | `DEPLOYER_SA` | `deployer@<project>.iam.gserviceaccount.com` |

   None of these are secret; the trust is in the pool's attribute condition. No Secret
   Manager secret is needed: the service and the eval both use Agent Platform.

A service account key in a `GCP_SA_KEY` secret (`credentials_json:` on the auth step)
also works, but it is a long-lived credential that can leak from CI. Use it only where
Workload Identity Federation is not possible, and rotate it.

## Run it

Locally first:

1. `cd Module_15_Deployment/11_github_actions_cicd`
2. `pytest tests -v`

If this passes locally with Agent Platform credentials, the CI test step will pass too.
Authentication is the only part you cannot try locally. To chat with the agent:
`adk web` from this folder, select `greet_agent`, send "Greet Priya".

In CI:

1. Copy `.github/workflows/deploy.yml` to `.github/workflows/` at your repository root
   and set `AGENT_DIR` in it to this folder's path.
2. Push to `main`, or run the workflow from the Actions tab (`workflow_dispatch`).

## What to look for

- In the Actions tab, a red `Run tests and eval gate` step means the deploy step never
  started. To see it, change the expected answer in `tests/greet.test.json` and push.
- The eval runs `num_runs=1` for cost. For an agent with more variance, raise it and
  accept the extra model calls per pipeline run.
- `adk deploy cloud_run` exits non-zero if the build or deploy fails, so the job fails
  too. The service URL is in the step log.

## Clean up

```bash
gcloud run services delete greet-agent --region=us-central1 --project="$GCP_PROJECT"
gcloud iam workload-identity-pools providers delete gh-provider \
  --workload-identity-pool=gh-pool --location=global --project="$GCP_PROJECT"
gcloud iam workload-identity-pools delete gh-pool --location=global --project="$GCP_PROJECT"
for ROLE in roles/run.sourceDeveloper roles/serviceusage.serviceUsageConsumer roles/aiplatform.user; do
  gcloud projects remove-iam-policy-binding "$GCP_PROJECT" \
    --member="serviceAccount:$DEPLOYER" --role="$ROLE"
done
gcloud iam service-accounts delete "$DEPLOYER" --project="$GCP_PROJECT"
```

Deleted pools stay recoverable for 30 days and their ids cannot be reused in that time.
Remove the workflow file and the three repository variables from GitHub.
