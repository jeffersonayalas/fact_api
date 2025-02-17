from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from db import session
from src.models.invoice_models import Facturas


app = FastAPI()



@app.get("/{id}")
async def get_fact(id: int):
    fact_query = session.query(Facturas).filter(Facturas.id == id)
    fact = fact_query.first()
    if fact is None:
        raise HTTPException(status_code = 404, detail="Not found")
    return fact



