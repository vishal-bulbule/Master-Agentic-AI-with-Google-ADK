adk deploy cloud_run \
    --project=tt-labs-001 \
    --region=us-central1 \
--service_name=adk-demo \
--app_name=content_creation_agent \
--with_ui \
./content_creation_agent

#create session
$ curl -X POST "https://adk-demo-539049793214.us-central1.run.app/apps/content_creation_agent/users/vish/sessions" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{}'
{"id":"3c8ca5e7-5392-425f-80ee-1d72f2c5b8a3","appName":"content_creation_agent","userId":"vish","state":{},"events":[],"lastUpdateTime":1759082849.5252614}

#Query
curl -N -X POST "https://adk-demo-539049793214.us-central1.run.app/run_sse" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{
        "app_name": "content_creation_agent",
        "user_id": "vish",
        "session_id": "3c8ca5e7-5392-425f-80ee-1d72f2c5b8a3",
        "newMessage": {
          "role": "user",
          "parts": [{ "text": "Create content on RAG" }]
        }
      }'