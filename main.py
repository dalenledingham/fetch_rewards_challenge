from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

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
spent_points = []


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


# Spend Route

@app.post("/spend/")
async def spend(points_to_spend: int):
    if points_to_spend > user_points:                                                               # if the user tries to spend more points than they have available
        raise HTTPException(status_code=400, detail="Not enough points")

    sorted_transactions = sorted(transactions, key=lambda x: x.timestamp) # sort transactions by timestamp
    
    for transaction in sorted_transactions:
        if points_to_spend > 0 and transaction.spent is False:                                      # if there are points left and this transaction is not spent

            if points_to_spend >= transaction.remaining_points:                                     # if there are more points left than this transaction has left

                if payers[transaction.payer] >= transaction.remaining_points:                       # if payer has more points than transaction
                    points_to_spend = spend_all_transaction_points(points_to_spend, transaction)

                else:                                                                               # if this transaction has more points than payer has left
                    points_to_spend = spend_all_payer_points(points_to_spend, transaction)

            elif payers[transaction.payer] >= transaction.remaining_points:                         # if payer has more points than transaction
                points_to_spend = spend_all_user_points(points_to_spend, transaction)

            elif payers[transaction.payer] >= points_to_spend:                                      # if payer has more points than there are left
                points_to_spend = spend_all_user_points(points_to_spend, transaction)

            else:                                                                                   # if there are more points left than this payer has left
                points_to_spend = spend_all_payer_points(points_to_spend, transaction)

    return spent_points


# Functions

def spend_all_transaction_points(points_to_spend: int, transaction: Transaction):
    global user_points
    payers[transaction.payer] -= transaction.remaining_points
    points_to_spend -= transaction.remaining_points
    user_points -= transaction.remaining_points

    add_spent_points(transaction.payer, transaction.remaining_points)

    transaction.remaining_points = 0
    transaction.spent = True
    return points_to_spend

def spend_all_payer_points(points_to_spend: int, transaction: Transaction):
    global user_points
    transaction.remaining_points -= payers[transaction.payer]
    points_to_spend -= payers[transaction.payer]
    user_points -= payers[transaction.payer]

    add_spent_points(transaction.payer, payers[transaction.payer])

    payers[transaction.payer] = 0
    return points_to_spend

def spend_all_user_points(points_to_spend: int, transaction: Transaction):
    global user_points
    transaction.remaining_points -= points_to_spend
    payers[transaction.payer] -= points_to_spend
    user_points -= points_to_spend

    add_spent_points(transaction.payer, points_to_spend)

    points_to_spend = 0
    return points_to_spend

def add_spent_points(payer: str, points: int):
    if any(payer in line_item for line_item in spent_points):
        spent_points[dict][payer] -= points
    else:
        spent_points.append({"payer": payer, "points": (0 - points)})

