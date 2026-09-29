"""Development server entry point."""

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "src.api:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
