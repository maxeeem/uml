# Deployment Debug Guide

## Issue: "The string did not match the expected pattern"

This error usually indicates one of two things:
1. **Browser Side:** A `DOMException` related to `atob` (Base64 decoding) failure.
2. **Server Side:** An error from the OpenAI Python library or `httpx` related to header validation (often caused by invalid characters in API keys).

## The Fix

I have updated `api/generate.py` to:
1. **Explicitly check** if `OPENAI_API_KEY` is loaded.
2. **Strip whitespace** more aggressively from the API key.
3. **Log detailed errors** to the Vercel console (stdout).
4. **Return the specific error message** to the client instead of masking it.

## Verification Steps

1. **Check Vercel Environment Variables:**
   - Go to your Vercel Project Settings > Environment Variables.
   - Verify `OPENAI_API_KEY` is set.
   - **Crucial:** Click "Edit" and ensure there are no hidden spaces, newlines, or quotes (e.g. `"sk-..."` should just be `sk-...`).
   - Ensure you didn't paste the Project ID or Organization ID by mistake.

2. **Re-deploy:**
   - Push these changes to your repository.
   - Wait for Vercel to build.

3. **Test:**
   - Open the deployed app.
   - Try to generate a diagram.
   - If it fails, look at the error message in the red box.
   - **Check Vercel Logs:** Go to Vercel Dashboard > Deployments > [Latest] > Logs. You will now see lines like:
     - `OpenAI API Key loaded (length: 51)`
     - `OpenAI API Error: ...`
     - `General Error: ...`

## If the error persists

If you still see "The string did not match the expected pattern" in the red box, it confirms the error is likely happening in the browser or is being passed through from the server specifically with that text. The new logs will definitively tell us which one it is.
