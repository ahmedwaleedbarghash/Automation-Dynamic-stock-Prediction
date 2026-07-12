You've got two great questions.

## 1. Why the 80/20 Split? (Train-Test Split)

Think of it like studying for an exam.

- **Training Data (80%):** This is your **textbook and homework**. The model studies this large chunk of data to learn all the patterns, trends, and relationships in the stock's price history.
    
- **Test Data (20%):** This is the **final exam**. It's data the model has **never seen before**. We use this to check if the model _actually_ learned the patterns or just _memorized_ the homework.
    

If we trained on 100% of the data, the model might get a perfect score, but only because it memorized the answers. This is called **overfitting**. When you show it a new day it's never seen, it will fail badly.

The 80/20 split is just a common-sense rule: use most of your data for learning (80%) and save a good portion for a fair, unseen test (20%).


The metrics you are seeing (like val_loss, MAE, and MAPE) are your accuracy.

Here’s the simple explanation:

For a problem like this, we don't use "accuracy" in the way you might think (like "85% correct"). That type of accuracy is for Classification problems (e.g., "Will the stock go UP or DOWN?").

Your model is doing a Regression problem (e.g., "What will the stock's price be?").

Why "Accuracy" Doesn't Work for Regression
Think about it:

If the real price is $150.50...

...and your model predicts $150.49...

Is the model "wrong"? According to a simple "accuracy" score, yes. But in reality, that's an excellent prediction.

That's why for regression, we measure accuracy by how small the error is.

Where to Find Your "Accuracy" in the Log
Here is how you should read your console log to find your model's "accuracy":

During Training (Epochs):

loss: 1.8801e-04: This is the error on the data the model trained on (its "practice test").

val_loss: 0.0018: This is your primary "accuracy" score during training. It's the error on the "unseen" validation data (the "real test"). The fact that this number got very small is a sign of a highly accurate model.

Final Evaluation (After Training):

MAE: 5.92: This is the clearest measure of your accuracy. It means, "On average, my model's price prediction is off by about $5.92." That's very accurate!

MAPE: 11.76%: This is the closest to a percentage score. It means, "On average, my model's prediction is off by about 11.76% of the real price."

So, you are seeing the accuracy. It's just expressed as a measure of error (how close the prediction is) rather than a simple "correct/incorrect" percentage. Your final result of MAE: 5.92 and MAPE: 11.76% shows your model is quite accurate!