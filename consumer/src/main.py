import uvicorn
from fastapi import FastAPI

app = FastAPI()


if __name__ == "__main__":
    uvicorn.run(app)
