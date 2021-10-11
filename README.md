# Fetch Rewards Coding Challenge

This is my submission for the coding challenge portion of the Fetch Rewards - Apprentice internview process. 

The objectives are stated in the [points.pdf](points.pdf) file. Please review them there. 

## Starting the app

To run this application via Bash shell, navigate to the project directory in your termnal and activate the virtual environment.  
> `source venv/bin/activate`

Then, run the app using the following command: 
> `uvicorn main:app`


In your browser, navigate to *localhost:8000/docs* to see the testing interface. 

## How to use the app

**Root** shows the running total of points the user has available to spend. To view the total user points, open the Root menu, click *Try it out* and then click *Execute*. The box labeled **Response Body** shows the output of the execution. 

**Create Payer** allows you to add a new payer and their starting points value. To create a payer, open the Create Payer menu, click *Try it out*, enter the payer's information in JSON format, and then click *Execute*. The box labeled **Response Body** shows the output of the execution. 
Example format: 
> {
  "name": "FETCH REWARDS", 
  "points": 0
}

**Get All Payers** will display all payers and their individual points values in JSON format. To view the list of payers, open the Get All Payers menu, click *Try it out* and then click *Execute*. The box labeled **Response Body** shows the output of the execution. 

**Create Transaction** allows you to add a new transaction with the following data: payer name, points value, timestamp, spent boolean (defaults to false, used for user spending), remaining points (forces equal to points value, used for user spending). To create a transaction, open the Create Transaction menu, click *Try it out*, enter the transaction's information in JSON format, and then click *Execute*. The box labeled **Response Body** shows the output of the execution. 
Example format: 
> {
  "payer": "FETCH REWARDS", 
  "points": 1000, 
  "timestamp": "2020-11-02T14:00:00+00:00", 
  "spent": false, 
  "remaining_points": 0
}

**Get All Transactions** will display all transactions including their payers, points values, and timestamps in the order they were added and in JSON format. To view the list of transactions, open the Get all Transactions menu, click *Try it out* and then click *Execute*. The box labeled **Response Body** shows the output of the execution. 

**Spend** allows you to spend points that the user has accumulated. The details for how points are spent are in the [points.pdf](points.pdf) file. Please review them there. To spend points, open the Spend menu, click *Try it out*, input the number of points you would like to spend, and then click *Execute*. 


