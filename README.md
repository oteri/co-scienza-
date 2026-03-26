# co-scienza-
co-scienza is an app to manage scientific knowledge.

# Google Cloud prerequisites (do this first, blocks everything else)
## Install gcloud CLI, then:
```bash
gcloud projects create co-scienza --name="co-scienza"
gcloud config set project co-scienza
gcloud services enable \
  drive.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com
```

## Create a service account for the backend

```bash
gcloud iam service-accounts create coscienza-backend \
  --display-name="co-scienza backend"

gcloud projects add-iam-policy-binding co-scienza \
  --member="serviceAccount:coscienza-backend@co-scienza.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud iam service-accounts keys create sa.json \
  --iam-account=coscienza-backend@co-scienza.iam.gserviceaccount.com
```

Then in the Google Cloud Console:
APIs & Services → Credentials → Create OAuth 2.0 Client ID (Web application)

Add http://localhost:8000/auth/callback as redirect URI

Copy the client ID + secret into .env
Billing must be enabled on the project for Vertex AI to work (it has a free tier, but billing must be on).
