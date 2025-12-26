import uvicorn
from apis import app
import os


def main():
    """Run the Brand Intelligence API."""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()