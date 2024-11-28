# Cerebro-Gradient_AI_Hackathon

## Problem Statement : 
Despite access to historical trading charts, traders lack an efficient tool to analyze and accurately predict future trends, leading to suboptimal decision-making. Furthermore, the absence of transparent systems reduces trust in trading predictions. Our solution leverages AI to provide reliable trend forecasts while integrating blockchain technology to ensure transparency and accountability in the prediction process

## Results:
We ran the tests overnight for ETHUSDT and BTCUSDT and we got the following results:For ETH:
It had a total of 20 buy orders and a total of 68 sell orders.
The average buy price for the orders came out to be $3644.52 and the average sell price came out to be $3653.61.

For BTC:
-It had a total of  buy orders and a total of 2 sell orders.
-The average buy price for the orders came out to be $96283.53 and the average sell price came out to be $96374.71.

Hence we can observe that, at an average we have bought the coin at a lower price and sold it at a higher price, usually for Futures trades we use a leverage, so at a high leverage of 25-30x , we will end up making a good profit on our trades.

![WhatsApp Image 2024-11-28 at 08 22 08_fffea8ee](https://github.com/user-attachments/assets/12a5979f-8d4e-4cc2-b3a5-f973710495e5)

## Changes Made After Results:
Initially in the results we could see that the number of buy or sell orders were more in number compared to the other order due to market sentiments, so we made changes in the code such that a buy order is followed strictly by a sell order hence making it easier for us to calculate the profit/loss percentage and also calculate the accuracy of our project.

We integrated the blockchain component in the project such that every time a buy or a sell call is made, it gets pushed into the blockchain and hence be immutable forever maintaining transparency. But we didn’t have any further calls after the implementation hence we couldn’t generate any transactions as of now.

To compensate for it, we had made it so that all the calls were getting saved in a csv file which has logged in all the data we got overnight and is been attached in the github repository.

## Future Scopes:

- Currently the model is checking if three of the five conditions are satisfied and hence a buy or a sell order is given as the output. If all five of the conditions are met, a Super Buy/ Super Sell call is made which will have the highest accuracy in all of the calls.
  
- We have made the code such that we would get short term gains in order to show the results, but to make it more accurate we can increase the timeline of the indicators hence giving the code a bigger timeline to work on and hence create more accurate results.

## Frontend:
![WhatsApp Image 2024-11-28 at 08 27 36_c9c1ff50](https://github.com/user-attachments/assets/04dc37ce-7b88-4a28-92b3-fcb95c452472)

![WhatsApp Image 2024-11-28 at 08 27 36_b4b658a2](https://github.com/user-attachments/assets/110d4252-bb5a-4bf4-8fc4-65968a93dbef)

![WhatsApp Image 2024-11-28 at 08 27 36_6933c974](https://github.com/user-attachments/assets/904def84-c813-44cc-91ee-64bbeceb72c7)

