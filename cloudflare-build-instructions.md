# Cloudflare Pages Deployment Instructions

## Build Command
For deploying this FastAPI application on Cloudflare Pages, use the following build command:

```
pip install -r requirements.txt && mkdir -p .output/server && cp -r app .output/server/ && cp run.py .output/server/
```

## Build Output Directory
Set the build output directory to:

```
.output
```

## Environment Variables
Add these environment variables in the Cloudflare Pages settings:

- `PYTHON_VERSION`: `3.11` (or your preferred Python version)
- `NODE_VERSION`: `16` (or higher)

## Additional Settings

### Functions Configuration
Create a `_routes.json` file in your project with the following content:

```json
{
  "version": 1,
  "include": ["/*"],
  "exclude": ["/static/*"]
}
```

### Entry Point Configuration
Create a `functions/_middleware.js` file with:

```javascript
export const onRequest = async ({ request, next, env }) => {
  try {
    return await next();
  } catch (err) {
    return new Response(`${err.message}\n${err.stack}`, { status: 500 });
  }
};
```

## Post-Deployment
After deployment, your FastAPI application will be available at your Cloudflare Pages URL. You may need to configure additional environment variables specific to your application in the Cloudflare Pages dashboard.