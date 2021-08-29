from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json

class Payer(BaseModel):
    name: str
    points: int = 0

class Transaction(BaseModel):
    payer: str
    points: int = 0
    timestamp: datetime
    spent: Optional[bool] = False
    temp_points: Optional[int] = 0

app = FastAPI()

user_points = 0
payers = {}
transactions = []


# Root Route

@app.get("/")
async def root():
    return user_points


# Payer Routes

@app.post("/payer/")
async def create_payer(payer: Payer):
    payers.update({payer.name: payer.points})
    return payer

@app.get("/payer/", response_model=Dict[str, int])
async def get_all_payers():
    return payers


# Transaction Routes

@app.post("/transaction/")
async def create_transaction(transaction: Transaction):
    try:
        if transaction.payer in payers.keys():
            global user_points
            transactions.append(transaction)
            payers[transaction.payer] += transaction.points
            user_points += transaction.points
            transaction.temp_points = transaction.points
            return transaction
        else:
            raise HTTPException
    except:
        raise HTTPException(status_code=404, detail="Payer not found")

@app.get("/transaction/", response_model=List[Transaction])
async def get_all_transactions():
    return transactions


# Spend Route

@app.post("/spend/")
async def spend(points_to_spend: int):
    global user_points
    spent_points = []
    sorted_transactions = sorted(transactions, key=lambda x: x.timestamp) # sort transactions by timestamp
    # for each transaction in sorted_transactions
    for transaction in sorted_transactions:
        # if there are points left to spend
        if points_to_spend > 0:
            # if the current transaction's points are not all spent
            if transaction.spent is False:
                # if there are more points to spend than this transaction has available
                if points_to_spend >= transaction.temp_points:
                    # if this transaction's payer has more points than this transaction has available
                    if payers[transaction.payer] >= transaction.temp_points:
                        payers[transaction.payer] -= transaction.temp_points
                        points_to_spend -= transaction.temp_points
                        user_points -= transaction.temp_points
                        transaction.temp_points = 0
                        transaction.spent = True
                    # if this transaction has more points than its payer has available
                    else:
                        transaction.temp_points -= payers[transaction.payer]
                        points_to_spend -= payers[transaction.payer]
                        user_points -= payers[transaction.payer]
                        payers[transaction.payer] = 0
                # if this transaction has more points than there are left to spend
                else:
                    # if this transactin's payer has more points than this transaction has available
                    if payers[transaction.payer] >= transaction.temp_points:
                        transaction.temp_points -= points_to_spend
                        payers[transaction.payer] -= points_to_spend
                        user_points -= points_to_spend
                        points_to_spend = 0
                    # if this transaction has more points than there are left to spend
                    else:
                        # if this transaction's payer has more points than there are left to spend
                        if payers[transaction.payer] >= points_to_spend:
                            transaction.temp_points -= points_to_spend
                            payers[transaction.payer] -= points_to_spend
                            user_points -= points_to_spend
                            points_to_spend = 0
                        # if there are more points left to spend than this transaction's payer has available
                        else:
                            transaction.temp_points -= payers[transaction.payer]
                            points_to_spend -= payers[transaction.payer]
                            user_points -= payers[transaction.payer]
                            payers[transaction.payer] = 0
    spent_points_json = json.dumps(spent_points)
    return spent_points_json

