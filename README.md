# Emojiify 😎

A fun Flask web app that converts text into emoji-rich versions.  
Now with user accounts, Stripe payments, and automatic Render deployment!

---

## 🚀 Deployment (Render + GitHub Actions)

1. **Push to GitHub**
   - Commit and push all code to your `main` branch.

2. **Connect to Render**
   - Go to [Render.com](https://render.com)
   - Click **"New Web Service"**
   - Connect your GitHub account and select the repo `akedechristine/emojiify`
   - Choose **Python 3.11** and use this start command:
     ```
     gunicorn app:app
     ```
   - Add environment variables:
     ```
     SECRET_KEY=your_secret_here
     STRIPE_PUBLIC_KEY=pk_test_...
     STRIPE_SECRET_KEY=sk_test_...
     STRIPE_WEBHOOK_SECRET=whsec_...
     DATABASE_URL=sqlite:///emojiify.db
     ```

3. **Enable GitHub Actions**
   - In your repo settings → Secrets → Actions:
     - Add `RENDER_API_KEY` (from your Render Dashboard → Account Settings)
     - Add `RENDER_SERVICE_ID` (from Render → your web service → Info tab)

4. **Automatic Deployment**
   - Every time you push to `main`, GitHub Actions will automatically deploy your latest version to Render 🎉

---

## 🧩 Local Testing

```
pip install -r requirements.txt
flask run
```

For Stripe testing:
```
stripe listen --forward-to localhost:5000/stripe/webhook
```

Use test card `4242 4242 4242 4242`.

---

## 🪙 Features
- Flask-Login user accounts
- Stripe payments with webhook verification
- Payment history page
- SQLite database for local & cloud testing
- Modern UI/UX ready for live deployment

---
