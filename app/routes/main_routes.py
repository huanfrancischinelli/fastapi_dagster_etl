from fastapi import APIRouter

main_routes = APIRouter()

@main_routes.get("/")
def read_root():
    return {"message": "FastAPI application created for teste_data_eng."}
