# Facebook & Instagram API Setup

This guide walks through setting up Facebook and Instagram APIs for the marketing automation platform: app creation, tokens, and (when implemented) publishing.

---

## 1. Prerequisites

- A **Facebook account**
- An **Instagram Business or Creator account** (for Instagram API; must be linked to a Facebook Page)
- A **Facebook Page** (required for Instagram Graph API and for posting to Facebook)

---

## 2. Create a Facebook Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com/).
2. Sign in with your Facebook account.
3. If prompted, complete **Developer Registration** (agree to terms, add a role if asked).

---

## 3. Create an App

1. In the top right, click **My Apps** → **Create App**.
2. Choose **Other** or **Business** (depending on what you see) → **Next**.
3. Select **Business** as the app type → **Next**.
4. Fill in:
   - **App Name**: e.g. `Marketing Automation Platform`
   - **App Contact Email**: your email
5. Click **Create App**.

---

## 4. Add Products

You need these products for read/sync and (later) publish:

1. In the app dashboard, go to **App Dashboard** (left sidebar) or **Add Products**.
2. Add:
   - **Instagram Graph API** – for Instagram Business accounts (posts, insights, and later publishing).
   - **Facebook Login** – for getting user/page tokens.
   - **Instagram Basic Display** – optional; for basic display if you use that flow.
3. For **Instagram Graph API**, you’ll need an Instagram Business or Creator account connected to a Facebook Page.  
   - In Meta Business Suite (business.facebook.com) or Page settings, connect your Instagram account to your Page if not already done.

---

## 5. App Settings (App ID & Secret)

1. In the app, go to **Settings** → **Basic**.
2. Note:
   - **App ID**
   - **App Secret** (click **Show** and copy).
3. Add **Privacy Policy URL** and **Terms of Service URL** if required (use placeholders for development, e.g. `https://example.com/privacy`).
4. **App Domains**: for local dev you can leave blank or add `localhost`; for production add your domain.

---

## 6. OAuth / Login Setup (for tokens)

1. Go to **Facebook Login** → **Settings** (under Products).
2. **Valid OAuth Redirect URIs**: add the URL your app uses after login, e.g.:
   - `http://localhost:8080/` (if you run a local callback server)
   - Your production callback URL when you deploy
3. Save changes.

---

## 7. Get Access Tokens

### Important: You always get a User token first

In **Graph API Explorer**, the "Reconnect" (or "Continue") flow **always** returns a **User** access token—even if you chose "Page Access Token" in the dropdown. That dropdown only controls which permissions are requested; it does **not** give you a Page token directly.

To post to a Page, you must use a **Page** access token. You get it in two steps:

1. **Get a User token** (with page permissions) from the Explorer.
2. **Call the API** with that User token to get the Page token (see below).

### Option A: Graph API Explorer (quick for testing)

1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer/).
2. Select your app from the **Meta App** dropdown.
3. Add permissions: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts` (use "Add a Permission" or the permissions list).
4. Click **Generate Access Token**. When the "Reconnect … to marketing-automation?" (or similar) dialog appears, click **Reconnect** (or **Continue**). You will receive a **User** token—this is expected.
5. **Get the Page token**: In the same Explorer, set the request to:
   - **GET** and endpoint: `v18.0/me/accounts`
   - Click **Submit**. The response is a list of Pages you manage. Each item has `id` (Page ID) and **`access_token`** (that Page’s token).
6. In the response, find your Page (e.g. "Test Test") and **copy that item’s `access_token`**. That is your **Page token**. Put it in `.env` as `FACEBOOK_ACCESS_TOKEN` and use the same Page’s `id` as `FACEBOOK_PAGE_ID`.

For **read** (sync) you typically need the same permissions; for **Instagram**, add `instagram_basic`, `instagram_manage_insights`, `instagram_content_publish` as needed.

### Long-lived tokens (recommended for automation)

- **User token**: Exchange the short-lived token for a long-lived one (about 60 days) via:
  - `GET https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_lived_token}`
- **Page token**: Use the long-lived user token to get a Page Access Token (from the `access_token` field in each item of `GET /v18.0/me/accounts?access_token={user_token}`), or for a single page:
  - `GET https://graph.facebook.com/v18.0/{page_id}?fields=access_token&access_token={user_token}`
- **Instagram**: For Instagram Graph API with Facebook Login, you use the **Page** that is linked to the Instagram account. The same Page token can be used for the Instagram Business Account linked to that Page. Get the Instagram Business Account ID:
  - `GET https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token={page_token}`  
  - The response contains `instagram_business_account.id`; that’s your **Instagram Business Account ID**.

---

## 8. Add Test Users (development only)

If your app is in **Development** mode, only **roles** (admins, developers, testers) and **test users** can use it.

1. Go to **App Roles** → **Roles** (in the app dashboard).
2. Add teammates as **Developers** or **Testers** (they use their own Facebook account).
3. Or go to **App Roles** → **Test Users** and create test users for automated tests.

For **Instagram/Facebook Login**, the accounts that sign in must be either:
- App admins/developers/testers, or  
- Test users of the app.

---

## 9. Environment Variables

Add to your `.env` (see `.env.example`):

```env
# Facebook App
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# Tokens (long-lived Page/User tokens; rotate as needed)
FACEBOOK_ACCESS_TOKEN=your_facebook_page_or_user_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token

# Optional: IDs for API calls
# Get from Graph API: Page ID, Instagram Business Account ID
# FACEBOOK_PAGE_ID=your_page_id
# INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_id
```

For **Instagram Graph API** (with Facebook Login), the same Page token is often used for both Facebook Page and linked Instagram Business Account. Store `instagram_business_account_id` in your app (e.g. from `channel_credentials` or config) when you have it.

---

## 10. Platform Status: Read vs Publish

| Feature | Status in this project |
|--------|-------------------------|
| **Setup & docs** | This guide + Section 6 in `TEAM_SETUP_GUIDE.md`. |
| **Read / sync** | Implemented. `InstagramIntegration` and `FacebookIntegration` sync account info, posts, insights. |
| **Publish / upload** | Not yet implemented. Execution handlers return a simulated `post_id`. |

### When we add Instagram publish

- **Instagram**: Create container (`POST /{ig-user-id}/media` with `image_url` or `video_url`), then publish (`POST /{ig-user-id}/media_publish` with `creation_id`). Media must be on a **public URL**. See [Content Publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing).
- **Facebook**: Publish a post to a Page via `POST /{page-id}/feed` (e.g. `message`, `link`, or photo/video).

---

## 11. Troubleshooting

### "Insufficient Developer Role" Error

**Error**: `Insufficient Developer Role: Insufficient developer role`

**Cause**: Your Facebook account doesn't have the right role in the app, or the app is in Development mode and your account isn't authorized.

**Quick Fix**:
1. Go to **App Roles** → **Roles** in your app dashboard
2. Ensure your Facebook account is listed as **Admin**, **Developer**, or **Tester**
3. If not, ask the app admin to add you (or add yourself if you're the admin)
4. Ensure your Instagram account is **Business/Creator** (not Personal) and linked to a Facebook Page
5. Ensure your Facebook account **manages** that Page (check Page Roles)
6. Regenerate your access token after fixing roles

**See**: `FIX_INSTAGRAM_DEVELOPER_ROLE.md` for detailed step-by-step instructions.

---

### "(#200) … requires both pages_read_engagement and pages_manage_posts as an admin with sufficient administrative permission"

**Error**: `403` when posting to a Page feed (`POST /{page-id}/feed`).

**Cause**: The token does not have both required permissions, or the Facebook user is not an admin with sufficient permission on the Page.

**Fix**:

1. **User token permissions**  
   In [Graph API Explorer](https://developers.facebook.com/tools/explorer/), select your app and **Generate Access Token**. In the permissions list, enable:
   - `pages_read_engagement`
   - `pages_manage_posts`  
   (and `pages_show_list` if you use it). Generate the token and accept the prompts.

2. **Get a Page token from that user token**  
   Call:  
   `GET /v18.0/me/accounts?access_token={USER_TOKEN}`  
   In the response, find your Page and copy its `access_token`. Use this **Page access token** in `FACEBOOK_ACCESS_TOKEN`.

3. **Page role**  
   The Facebook account that generated the token must be an **Admin** (or a role with “Create content” / full management) on the Page. Check **Page settings → Page access** and ensure your account has admin (or equivalent) access.

4. **App roles**  
   If the app is in Development mode, that same account must be an **Admin**, **Developer**, or **Tester** of the app (**App roles** in the app dashboard).

After changing permissions or roles, generate a new user token (with both permissions), then a new Page token from it, and update `.env`.

---

### Other Common Issues

- **"App not in development" / "User not authorized"**: Ensure the Facebook/Instagram account is an app admin/developer/tester or a test user.
- **Invalid OAuth redirect**: Add the exact callback URL to **Facebook Login** → **Settings** → **Valid OAuth Redirect URIs**.
- **Missing permissions**: In Graph API Explorer, request the right permissions and regenerate the token; then exchange for a long-lived token if needed.
- **Instagram "This account is not a business account"**: Convert the Instagram account to Business/Creator and connect it to a Facebook Page in Meta Business Suite.

For more on tokens and permissions, see [Meta’s Access Token docs](https://developers.facebook.com/docs/facebook-login/guides/access-tokens) and [Instagram Graph API Overview](https://developers.facebook.com/docs/instagram-platform/overview).
