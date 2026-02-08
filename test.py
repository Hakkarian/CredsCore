import joblib
import pandas as pd

high_risk_client = {
    'RevolvingUtilizationOfUnsecuredLines': 0.95,  # 95% high usage of credit limits
    'age': 22,                                    
    'NumberOfTime30-59DaysPastDueNotWorse': 3,    
    'DebtRatio': 1.8,                            
    'MonthlyIncome': 1500.0,                    
    'NumberOfOpenCreditLinesAndLoans': 10,       
    'NumberOfTimes90DaysLate': 1,                 
    'NumberRealEstateLoansOrLines': 0,            
    'NumberOfTime60-89DaysPastDueNotWorse': 1,    
    'NumberOfDependents': 3.0                     
}

model = joblib.load('saved_models/lightgbm_credit_model.pkl')

client_df = pd.DataFrame([high_risk_client])

default_prob = round(model.predict_proba(client_df)[0][1], 3)
predicted_class = model.predict(client_df)[0]

if(default_prob < 0.1):
    print("Approved!")
else:
    print("Declined!")

print(f"Default probability: {default_prob:.2%}")