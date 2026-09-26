<!-- Author: Vishal Bulbule -->
<!-- Date: 2026-09-22 -->

# 07 - Cloud Build Permissions

## What this shows

The most common reason a first source deploy fails. `adk deploy cloud_run` and
`gcloud run deploy --source .` build the container with Cloud Build, and on projects
created with current defaults the build runs as the default compute service account,
`<PROJECT_NUMBER>-compute@developer.gserviceaccount.com`, which has no build role.

The symptom:

```
ERROR: (gcloud.run.deploy) PERMISSION_DENIED: Build failed because the default service
account is missing required IAM permissions.
```

or a 403 mentioning `cloudbuild.builds.create` or `storage.objects.get`.

## Prerequisites

- The gcloud CLI logged in (`gcloud auth login`) and the Cloud Build API on:

  ```bash
  export GCP_PROJECT=your-project-id
  gcloud services enable cloudbuild.googleapis.com --project="$GCP_PROJECT"
  ```

- IAM for your own account: permission to change project IAM policy,
  `roles/resourcemanager.projectIamAdmin` (Owners have it).

## Run it

This changes IAM in your project.

1. `cd Module_15_Deployment/07_cloud_build_perms`
2. `export GCP_PROJECT=your-project-id`
3. `bash grant_cloudbuild_perms.sh`

The raw command it runs:

```bash
gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
```

The service account email uses the project number, not the project id; the script looks
it up with `gcloud projects describe`.

## What to look for

Verify the binding:

```bash
PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
gcloud projects get-iam-policy "$GCP_PROJECT" \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:${PROJECT_NUM}-compute@developer.gserviceaccount.com"
```

You do not need `roles/run.admin` on this account. Deploying the revision is done with
your own credentials (or your CI deployer's). The compute account is also the default
runtime identity of every Cloud Run service, so anything granted to it is granted to
your running agents too.

## How a source deploy works

1. The CLI packages your folder (for `adk deploy`, it first generates a Dockerfile).
2. It uploads the source to a Cloud Storage staging bucket.
3. Cloud Build builds the image, running as the build service account.
4. The image is pushed to Artifact Registry (`cloud-run-source-deploy` repository).
5. Cloud Run deploys a new revision from the image. This step runs as you.

Step 3 and 4 need `roles/cloudbuild.builds.builder` on the build service account. That
role already includes the Artifact Registry upload and log-writing permissions.

## Going further: separate identities

For production, use one service account per job:

- a build service account with only `roles/cloudbuild.builds.builder` (or the
  Cloud Run specific `roles/run.builder`), passed with `gcloud run deploy --build-service-account`;
- a runtime service account per service with only what the agent calls
  (`roles/aiplatform.user`, `roles/secretmanager.secretAccessor` on its secrets),
  passed with `--service-account`.

Then a compromised build cannot act as your agents, and one agent cannot read another
agent's secrets.

## Clean up

Remove the role when you no longer deploy from source in this project:

```bash
PROJECT_NUM=$(gcloud projects describe "$GCP_PROJECT" --format="value(projectNumber)")
gcloud projects remove-iam-policy-binding "$GCP_PROJECT" \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
```
