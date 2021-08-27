from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class Payer(BaseModel):
    name: str
    points: int = 0

class Transaction(BaseModel):
    id: int
    payer: str
    points: int = 0
    timestamp: datetime
    spent: bool = False

app = FastAPI()

user_points = 0
payers = {}
transactions = []

@app.get("/")
async def root():
    return user_points

# CRUD Payer

@app.post("/payer/")
async def create_payer(payer: Payer):
    payers.update({payer.name: payer.points})
    return payer

@app.get("/payer/", response_model=Dict[str, int])
async def get_all_payers():
    return payers

# @app.get("/payer/{name}")
# async def get_payer(name: str):
#     try:
#         return payers.get(name)
#     except:
#         raise HTTPException(status_code=404, detail="Payer not found")

# @app.put("/payer/{name}")
# async def update_payer(name: str, points: int):
#     try:
#         if name in payers.keys():
#             payers[name] = points
#             return payers[name]
#         else: 
#             raise HTTPException
#     except:
#         raise HTTPException(status_code=404, detail="Payer not found")

# @app.delete("/payer/{name}")
# async def delete_payer(name: str):
#     try:
#         if name in payers.keys():
#             obj = payers[name]
#             del payers[name]
#             return obj
#         else:
#             raise HTTPException
#     except:
#         raise HTTPException(status_code=404, detail="Payer not found")

# CRUD Transaction

@app.post("/transaction/")
async def create_transaction(transaction: Transaction):
    try:
        if transaction.payer in payers.keys():
            transactions.append(transaction)
            payers[transaction.payer] += transaction.points
            # user_points += transaction.points
            return transaction
        else:
            raise HTTPException
    except:
        raise HTTPException(status_code=404, detail="Payer not found")

@app.get("/transaction/", response_model=List[Transaction])
async def get_all_transactions():
    return transactions

# @app.get("/transaction/{id}")
# async def get_transaction(id: int):
#     try:
#         return transactions[id]
#     except:
#         raise HTTPException(status_code=404, detail="Transaction not found")

# @app.put("/transaction/{id}")
# async def update_transaction(id: int, transaction: Transaction):
#     try:
#         transactions[id] = transaction
#         return transactions[id]
#     except:
#         raise HTTPException(status_code=404, detail="Transaction not found")

# @app.delete("/transaction/{id}")
# async def delete_transaction(id: int):
#     try:
#         obj = transactions[id]
#         transactions.pop(id)
#         return obj
#     except:
#         raise HTTPException(status_code=404, detail="Transaction not found")

@app.post("/spend/")
async def spend(points_to_spend: int):
    sorted_transactions = sorted(transactions, key=lambda x: x.timestamp) # sort transactions by timestamp
    for transaction in sorted_transactions:
        # if points still left to spend
        if points_to_spend > 0:
            # if spending all of this transaction's points will not make payer balance negative
            if payers[transaction.payer] - transaction.points <= 0:
                payers[transaction.payer] -= transaction.points # adjust payer balance
                # user_points -= transaction.points # adjust user balance
                points_to_spend -= transaction.points # adjust points left to spend
                # if transaction has no points left to spend
                if transaction.points == 0:
                    transaction.spent = True
            else:
                # TODO: what to do if transaction's points would make payer balance negative
                # TODO: what to do if transaction's points greater than points left to spend
                break # placeholder
        else:
            continue
    return sorted_transactions


# track points balance per payer using dict
# on spend, loop through sorted non-spent transactions and subtract spent points from transaction's payer
# if transaction has negative points value, "spend" it by giving those points back to the payer

