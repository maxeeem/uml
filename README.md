# AI Diagram Generator

A Flask-based web application that generates PlantUML diagrams from natural language descriptions using OpenAI's GPT-4o-mini with structured outputs.

## Local Development

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key (required):
```env
OPENAI_API_KEY=sk-your-api-key-here
```

4. (Optional) Set access code in `.env` for local testing:
```env
ACCESS_CODE=your-secret-code
```
**Note:** If `ACCESS_CODE` is not set or is empty in `.env`, the access code check will be **disabled** for localhost.

### Run Locally

Start the development server:
```bash
python app.py
```

The app will be available at `http://localhost:8000`

**Note:** If port 8000 is in use, you can specify a different port:
```bash
PORT=8001 python app.py
```

### Access Code Behavior

- **Localhost (default):** Access code check is **DISABLED** - you can leave the access code field empty
- **Production (Vercel):** Access code check is **ENABLED** - you must set `ACCESS_CODE` environment variable in Vercel

## Deployment to Vercel

**📖 For detailed step-by-step instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

### Quick Steps:

1. **Initialize Git and push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   # Create a repo on GitHub, then:
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "Add New Project" → Import your GitHub repository
   - Add environment variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `ACCESS_CODE`: Your secret password (required for production)
   - Click "Deploy"

3. **Done!** Your app will be live at `https://your-project.vercel.app`

**Note:** Remember to set `ACCESS_CODE` in Vercel - this protects your API from unauthorized use in production!

## Project Structure

```
uml/
├── api/
│   └── generate.py      # Flask API endpoint (works for both local and Vercel)
├── public/
│   └── index.html       # Frontend HTML
├── app.py               # Local development server
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── README.md           # This file
```
