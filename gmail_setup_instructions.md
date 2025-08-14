# Gmail OAuth Setup Instructions

To enable the Email Summarizer agent functionality, you need to set up Gmail OAuth credentials.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

## Step 2: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:5000/orgs/{org_slug}/agents/{agent_id}/gmail/callback`
   - `http://127.0.0.1:5000/orgs/{org_slug}/agents/{agent_id}/gmail/callback`
   - Replace with your actual domain in production

## Step 3: Add Environment Variables

Add these to your `.env` file:

```
GMAIL_CLIENT_ID=your_client_id_here
GMAIL_CLIENT_SECRET=your_client_secret_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 4: Install Required Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client openai
```

## Step 5: Test the Integration

1. Create an Email Summarizer agent
2. Click on the agent name to view details
3. Click "Connect Gmail Account"
4. Complete the OAuth flow
5. Select email criteria and click "Fetch & Summarize Emails"

## Current Status

- ✅ Agent creation with redirect to agents page
- ✅ Clickable agent names leading to detail page
- ✅ Gmail OAuth flow setup
- ✅ Email summarization interface
- 🔄 Mock data currently returned (real Gmail API integration pending)
- 🔄 OpenAI summarization (pending real implementation)

## Next Steps

The basic infrastructure is in place. To complete the implementation:

1. Set up the environment variables above
2. The Gmail API integration and OpenAI summarization can be implemented when ready
3. Currently returns mock email summaries for testing the UI
