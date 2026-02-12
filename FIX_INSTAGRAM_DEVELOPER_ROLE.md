# Fix: Insufficient Developer Role (Instagram)

## Error Message
```
Insufficient Developer Role: Insufficient developer role
```

This error occurs when the Facebook account you're using doesn't have the right role in your Facebook App, or the app is in Development mode and your account isn't authorized.

---

## Solution Steps

### Step 1: Check Your Facebook App Mode

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Select your app from **My Apps**
3. Check the app status at the top:
   - **Development Mode**: Only admins/developers/testers can use it
   - **Live Mode**: Public (requires app review for production)

If it says **Development Mode**, proceed to Step 2.

---

### Step 2: Add Yourself as a Developer/Admin

**Option A: You created the app**
- If you created the app, you're already the **Admin**. Skip to Step 3.

**Option B: Someone else created the app**
1. In your app dashboard, go to **App Roles** → **Roles** (left sidebar)
2. Click **Add People**
3. Enter the **Facebook email** or **Facebook profile name** of the account you're using
4. Select role: **Developer** or **Admin**
5. Click **Add**
6. The person will receive a notification; they need to accept it

---

### Step 3: Verify Your Role

1. In the app dashboard, go to **App Roles** → **Roles**
2. Confirm your Facebook account is listed as **Admin**, **Developer**, or **Tester**
3. If not listed, ask the app admin to add you (see Step 2)

---

### Step 4: Ensure Instagram Account is Linked to Facebook Page

The Instagram account you're connecting must be:
- An **Instagram Business** or **Creator** account (not Personal)
- **Linked to a Facebook Page** that you manage

**To check/link:**
1. Go to [business.facebook.com](https://business.facebook.com/) (Meta Business Suite)
2. Select your **Page**
3. Go to **Settings** → **Instagram** (or **Page Settings** → **Instagram**)
4. If not linked, click **Connect Instagram Account** and follow the prompts
5. Ensure the Instagram account is set to **Business** or **Creator** (not Personal)

**To convert Instagram to Business:**
1. Open Instagram app → **Settings** → **Account**
2. Tap **Switch to Professional Account**
3. Choose **Business** or **Creator**
4. Connect it to your Facebook Page

---

### Step 5: Use the Correct Facebook Account

When connecting Instagram:
- Use the **same Facebook account** that has the Developer/Admin role in your app
- The Facebook account must **manage the Facebook Page** that's linked to the Instagram account

**To check Page roles:**
1. Go to your Facebook Page
2. Click **Settings** → **Page Roles**
3. Confirm your Facebook account is listed as **Admin** or **Editor**

---

### Step 6: Regenerate Access Token

After fixing roles, regenerate your access token:

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from **Meta App** dropdown
3. Click **Generate Access Token**
4. Select permissions:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_show_list`
   - `pages_read_engagement`
5. Generate token
6. Exchange for long-lived token (see `FACEBOOK_INSTAGRAM_API_SETUP.md` Section 7)
7. Update your `.env` with the new token

---

### Step 7: Test Connection Again

Try connecting your Instagram account again. The error should be resolved if:
- ✅ Your Facebook account has Developer/Admin/Tester role in the app
- ✅ Your Instagram account is Business/Creator and linked to a Facebook Page
- ✅ Your Facebook account manages that Page
- ✅ You're using a valid access token with the right permissions

---

## Common Mistakes

1. **Using a different Facebook account**: The account connecting Instagram must be the one with the Developer role.
2. **Personal Instagram account**: Must be Business or Creator.
3. **Instagram not linked to Page**: The Instagram account must be connected to a Facebook Page.
4. **Wrong Page**: The Page linked to Instagram must be managed by your Facebook account.
5. **Expired token**: Regenerate the token after fixing roles.

---

## Still Not Working?

1. **Check app status**: Ensure the app isn't restricted or disabled
2. **Check Instagram account**: Verify it's Business/Creator and linked to Page
3. **Check Page roles**: Your Facebook account must manage the Page
4. **Try Graph API Explorer**: Test the connection manually:
   ```
   GET /{page_id}?fields=instagram_business_account&access_token={your_token}
   ```
5. **Check error details**: Look for specific error codes in the API response

For more help, see `FACEBOOK_INSTAGRAM_API_SETUP.md` Section 11 (Troubleshooting).
