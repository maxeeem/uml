# Deployment Guide

## Prerequisites

1. **GitHub Account** - You'll need to push your code to GitHub
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free tier is fine)
3. **OpenAI API Key** - You should already have this from local development

## Step-by-Step Deployment

### 1. Initialize Git Repository (if not already done)

```bash
# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit: AI Diagram Generator"
```

### 2. Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `uml-diagram-generator` (or whatever you prefer)
3. **Don't** initialize with README, .gitignore, or license (we already have these)
4. Copy the repository URL (e.g., `https://github.com/yourusername/uml-diagram-generator.git`)

### 3. Push Code to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/uml-diagram-generator.git

# Push your code
git branch -M main
git push -u origin main
```

### 4. Deploy to Vercel

#### Option A: Via Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in (or sign up)
2. Click **"Add New..."** → **"Project"**
3. Click **"Import Git Repository"**
4. Select your GitHub repository (`uml-diagram-generator`)
5. Vercel will auto-detect the project settings:
   - **Framework Preset:** Other
   - **Root Directory:** `./` (leave as default)
   - **Build Command:** Leave empty (Vercel handles Python automatically)
   - **Output Directory:** Leave empty
6. Click **"Environment Variables"** and add:
   - `OPENAI_API_KEY` = `sk-your-actual-api-key-here`
   - `ACCESS_CODE` = `YourSecretPassword123` (choose a strong password)
7. Click **"Deploy"**

#### Option B: Via Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (from project root)
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? uml-diagram-generator (or your choice)
# - Directory? ./
# - Override settings? No

# Add environment variables
vercel env add OPENAI_API_KEY
# Paste your API key when prompted

vercel env add ACCESS_CODE
# Enter your secret access code when prompted

# Deploy to production
vercel --prod
```

### 5. Verify Deployment

1. After deployment completes, Vercel will give you a URL like:
   - `https://uml-diagram-generator.vercel.app`
2. Visit the URL and test:
   - Enter a description (e.g., "A simple user authentication system")
   - Enter your access code (the one you set in `ACCESS_CODE`)
   - Click "Generate"
   - Verify the diagram appears
   - Try editing the PlantUML code and clicking "Redraw Diagram"

### 6. Custom Domain (Optional)

1. In Vercel dashboard, go to your project → **Settings** → **Domains**
2. Add your custom domain
3. Follow DNS configuration instructions

## Important Notes

### Environment Variables

- **`OPENAI_API_KEY`**: Required - Your OpenAI API key
- **`ACCESS_CODE`**: Required for production - This protects your API from unauthorized use

### Access Code Security

- **In Production**: The access code check is **ENABLED** - users must enter the correct code
- **In Localhost**: The access code check is **DISABLED** by default (unless you set `ACCESS_CODE` in `.env`)

### Updating Your Deployment

After making changes:

```bash
git add .
git commit -m "Your commit message"
git push
```

Vercel will automatically detect the push and redeploy your application.

## Troubleshooting

### Build Fails

- Check that `requirements.txt` includes all dependencies
- Verify `vercel.json` is correct
- Check Vercel build logs for specific errors

### API Returns 403 "Incorrect Access Code"

- Verify `ACCESS_CODE` environment variable is set in Vercel
- Make sure you're entering the exact same code (case-sensitive)

### Diagram Doesn't Render

- Check browser console for errors
- Verify OpenAI API key is correct
- Check Vercel function logs: Project → **Functions** → Click on a function → View logs

### Can't Access `/api/render` Endpoint

- Verify `vercel.json` includes the `/api/render` route
- Check that both routes point to `api/generate.py`

## Cost Considerations

- **Vercel**: Free tier includes generous limits for serverless functions
- **OpenAI**: Pay per API call (GPT-4o-mini is very affordable)
- Monitor usage in both Vercel and OpenAI dashboards
