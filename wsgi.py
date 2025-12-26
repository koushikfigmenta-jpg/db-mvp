from apis import app

# Vercel serverless functions need this
async def asgi_handler(request):
    return app