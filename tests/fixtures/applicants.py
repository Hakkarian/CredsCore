VERY_LOW_RISK_APPLICANT = {
    "RevolvingUtilizationOfUnsecuredLines": 0.05,
    "age": 60,
    "NumberOfTime30_59DaysPastDueNotWorse": 0,
    "DebtRatio": 0.15,
    "MonthlyIncome": 20000.0,
    "NumberOfOpenCreditLinesAndLoans": 8,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 2,
    "NumberOfTime60_89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 2
}

MEDIUM_RISK_APPLICANT = {
    "RevolvingUtilizationOfUnsecuredLines": 0.45,
    "age": 40,
    "NumberOfTime30_59DaysPastDueNotWorse": 1,
    "DebtRatio": 0.55,
    "MonthlyIncome": 7500.0,
    "NumberOfOpenCreditLinesAndLoans": 10,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 3,
    "NumberOfTime60_89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 3
}

VERY_HIGH_RISK_APPLICANT = {
    "RevolvingUtilizationOfUnsecuredLines": 1.5,
    "age": 22,
    "NumberOfTime30_59DaysPastDueNotWorse": 8,
    "DebtRatio": 4.0,
    "MonthlyIncome": 1500.0,
    "NumberOfOpenCreditLinesAndLoans": 2,
    "NumberOfTimes90DaysLate": 5,
    "NumberRealEstateLoansOrLines": 0,
    "NumberOfTime60_89DaysPastDueNotWorse": 4,
    "NumberOfDependents": 0
}

THIN_FILE_YOUNG_APPLICANT = {
    "RevolvingUtilizationOfUnsecuredLines": 0.2,
    "age": 21,
    "NumberOfTime30_59DaysPastDueNotWorse": 0,
    "DebtRatio": 0.3,
    "MonthlyIncome": 3500.0,
    "NumberOfOpenCreditLinesAndLoans": 2,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 0,
    "NumberOfTime60_89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 0
}

SENIOR_HIGH_INCOME_APPLICANT = {
    "RevolvingUtilizationOfUnsecuredLines": 0.08,
    "age": 68,
    "NumberOfTime30_59DaysPastDueNotWorse": 0,
    "DebtRatio": 0.2,
    "MonthlyIncome": 25000.0,
    "NumberOfOpenCreditLinesAndLoans": 12,
    "NumberOfTimes90DaysLate": 0,
    "NumberRealEstateLoansOrLines": 4,
    "NumberOfTime60_89DaysPastDueNotWorse": 0,
    "NumberOfDependents": 1
}

TEST_CASES = {
    "Very Low Risk (Excellent Credit)": VERY_LOW_RISK_APPLICANT,
    "Medium Risk": MEDIUM_RISK_APPLICANT,
    "Very High Risk (Poor Credit)": VERY_HIGH_RISK_APPLICANT,
    "Thin File Young Applicant": THIN_FILE_YOUNG_APPLICANT,
    "Senior High Income": SENIOR_HIGH_INCOME_APPLICANT
}