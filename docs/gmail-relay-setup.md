# Gmail confirmation email relay

The bot sends confirmation emails through a private Google Apps Script web app.
The script runs as the Gmail account that deploys it, while Railway calls the
script over HTTPS. No SMTP password or custom domain is required.

## Create and authorize the script

1. Sign in at [script.google.com](https://script.google.com/) as
   `meserettse47@gmail.com` and create a new standalone project.
2. Copy the contents of [`scripts/gmail_relay.gs`](../scripts/gmail_relay.gs)
   into the Apps Script editor and save.
3. Open **Project Settings** → **Script Properties** and add:
   - Property: `GMAIL_RELAY_SECRET`
   - Value: a newly generated, long random secret
4. Select `authorizeMailSending` in the editor and click **Run**. Review and
   approve the Google permission request while signed in as the sender account.
5. Choose **Deploy** → **New deployment** → gear icon → **Web app**:
   - **Execute as:** Me
   - **Who has access:** Anyone
6. Deploy and copy the web app URL ending in `/exec`. Do not share the URL or
   relay secret publicly.

## Configure Railway

In the bot service's production environment, set:

| Variable | Value |
| --- | --- |
| `GMAIL_RELAY_URL` | The deployed Apps Script `/exec` URL |
| `GMAIL_RELAY_SECRET` | The same random secret stored in Script Properties |
| `EMAIL_FROM_NAME` | `ESF 2026 Comprehensive Stroke Care Symposium` |

The Gmail account that owns the deployed script is the sender. Replies are
directed to `ethiopiastrokefoundation@gmail.com`. After deploying the bot code
and applying these variables, register using an email inbox you can check.

Apps Script enforces daily email-recipient quotas. Google's current quota for a
consumer Gmail account is 100 recipients per day; quotas can change. Keep the
relay URL and secret private. If the secret is exposed, replace it in both
Apps Script Script Properties and Railway.
