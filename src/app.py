import uvicorn
from fastapi import FastAPI
from routers import search

app = FastAPI(title="iStock API", version="1.0.0")
app.include_router(search.router)

 
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8015, debug=True)
