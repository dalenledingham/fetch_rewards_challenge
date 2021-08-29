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
    remaining_points: Optional[int] = 0

app = FastAPI()

user_points = 0
payers = {}
transactions = []


# Root Route

@app.get("/")
async def root():
    return {"user points": user_points}


# Payer Routes

@app.post("/new-payer/")
async def create_payer(payer: Payer):
    payers.update({payer.name: payer.points})
    return payer

@app.get("/payers/", response_model=Dict[str, int])
async def get_all_payers():
    return payers


# Transaction Routes

@app.post("/new-transaction/")
async def create_transaction(transaction: Transaction):
    try:
        if transaction.payer in payers.keys():
            global user_points
            transactions.append(transaction)
            payers[transaction.payer] += transaction.points
            user_points += transaction.points
            transaction.remaining_points = transaction.points
            return transaction
        else:
            raise HTTPException
    except:
        raise HTTPException(status_code=404, detail="Payer not found")

@app.get("/transactions/", response_model=List[Transaction])
async def get_all_transactions():
    return transactions

global global_points
global_points = 0
# Spend Route

@app.post("/spend/")
async def spend(points_to_spend: int):
    global user_points
    global spent_points
    global global_points
    global_points = points_to_spend
    spent_points = {}
    sorted_transactions = sorted(transactions, key=lambda x: x.timestamp) # sort transactions by timestamp

    # if the user tries to spend more points than they have available
    if points_to_spend > user_points:
        raise HTTPException(status_code=400, detail="You do not have enough points")
    
    # for each transaction in sorted_transactions
    for transaction in sorted_transactions:
        # if there are points left to spend
        if global_points > 0 and transaction.spent is False:
        
            # if there are more points to spend than this transaction has available
            if global_points >= transaction.remaining_points:
                # if this transaction's payer has more points than this transaction has available - SPEND ALL TRANSACTION
                if payers[transaction.payer] >= transaction.remaining_points:
                    global_points = spend_all_transaction_points(global_points, transaction)

                # if this transaction has more points than its payer has available - SPEND ALL PAYER
                else:
                    global_points = spend_all_payer_points(global_points, transaction)

            # if this transaction has more points than there are left to spend
            else:
                # if this transactin's payer has more points than this transaction has available - SPEND ALL REMAINING
                if payers[transaction.payer] >= transaction.remaining_points:
                    global_points = spend_all_user_points(global_points, transaction)

                # if this transaction has more points than there are left to spend
                else:
                    # if this transaction's payer has more points than there are left to spend - SPEND ALL REMAINING
                    if payers[transaction.payer] >= global_points:
                        global_points = spend_all_user_points(global_points, transaction)

                    # if there are more points left to spend than this transaction's payer has available - SPEND ALL PAYER
                    else:
                        global_points = spend_all_payer_points(global_points, transaction)

    spent_points_json = json.dumps(spent_points)
    return spent_points_json


# Functions

def spend_all_transaction_points(points_to_spend: int, transaction: Transaction):
    global user_points
    payers[transaction.payer] -= transaction.remaining_points
    points_to_spend -= transaction.remaining_points
    user_points -= transaction.remaining_points
    transaction.remaining_points = 0
    transaction.spent = True
    return points_to_spend

def spend_all_payer_points(points_to_spend: int, transaction: Transaction):
    global user_points
    transaction.remaining_points -= payers[transaction.payer]
    points_to_spend -= payers[transaction.payer]
    user_points -= payers[transaction.payer]
    payers[transaction.payer] = 0
    return points_to_spend

def spend_all_user_points(points_to_spend: int, transaction: Transaction):
    global user_points
    transaction.remaining_points -= points_to_spend
    payers[transaction.payer] -= points_to_spend
    user_points -= points_to_spend
    points_to_spend = 0
    return points_to_spend

def add_spent_points(payer: str, points: int):
    global spent_points
    if payer in spent_points:
        spent_points.payer -= points
    else:
        spent_points.update({"payer": payer, "points": 0 - points})
    return spent_points