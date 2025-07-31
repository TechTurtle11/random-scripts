import datetime

def get_mandatory_payment(income, threshold, percentage=9) -> float:
    affected_amount = (income - threshold)/12
    return ((percentage / 100)) * affected_amount


def update_annual(income: float, annual_growth_percent: float):
    return income * (1 + (annual_growth_percent / 100))



def month(loan_value: float, income: float, direct_debit: float, threshold: float, annual_loan_interest_rate: float):

    mandatory = get_mandatory_payment(income, threshold)

    interest = ((annual_loan_interest_rate / 100)/ 12) * loan_value
    loan_value += interest
    new_loan =  loan_value - mandatory - direct_debit

    return new_loan


start_date = datetime.date(2023,5,22)
expiry_date = start_date + datetime.timedelta(days=365*30)

def get_months_until_loan_payed_off(current_date: datetime.date, loan_value: float, income: float, direct_debit: float, threshold: float, annual_loan_interest_rate: float, income_growth_percent: float, threshold_change_percent: float):
    months = 0
    total_payed = 25000


    while loan_value > 0:
        months += 1
        current_date += datetime.timedelta(days=365//12)
        if current_date > expiry_date:
            print("Loan not payed off in 30 years, exiting.")
            return months, total_payed

        loan_value = month(loan_value, income, direct_debit, threshold, annual_loan_interest_rate)
        total_payed += get_mandatory_payment(income, threshold) + direct_debit

        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

    return months,total_payed


def calculate_investment_growth(initial_investment: float, monthly_contribution: float, annual_interest_rate: float, months: int) -> float:
    total = initial_investment
    monthly_interest_rate = (annual_interest_rate / 100) / 12

    for _ in range(months):
        total += monthly_contribution
        total *= (1 + monthly_interest_rate)

    return total

def calc_loan_payed_off():

    start_date = datetime.datetime.now().date()

    loan_value = 43050.33
    income = 60000
    investment = 330 + 750
    direct_debit = 500
    threshold = 28470
    annual_loan_interest_rate = 7.3
    income_growth_percent = 3
    threshold_change_percent = 0

    print(f"Loan Value: £{loan_value:.2f}")
    print(f"Income: £{income:.2f} (growing at {income_growth_percent}% annually)")
    print(f"Direct Debit: £{direct_debit:.2f}")
    print(f"Threshold: £{threshold:.2f} (growing at {threshold_change_percent}% annually)")
    print(f"Annual Loan Interest Rate: {annual_loan_interest_rate}%")
    print(f"Investment Per Month: £{investment:.2f} (roi at an average rate of 5% annually)")
    print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    print("Calculating months until loan is paid off...")

    months,cost = get_months_until_loan_payed_off(start_date, loan_value, income, direct_debit, threshold, annual_loan_interest_rate, income_growth_percent,threshold_change_percent)
    years = months // 12
    remaining_months = months % 12
    date_payed_off = start_date + datetime.timedelta(days=months * 30)

    print(f"Loan will be paid off in {years} years and {remaining_months} months. Total cost: £{cost:.2f}")
    print(f"Expected date of loan payoff: {date_payed_off.strftime('%Y-%m-%d')}")

    investment_growth = calculate_investment_growth(investment, investment, 5, months)

    after_30_years = calculate_opportunity_costs(date_payed_off, direct_debit+investment, income, income_growth_percent, threshold, threshold_change_percent)

    print(f"Total gained after 30 years: £{investment_growth + after_30_years:.2f}")




def calculate_opportunity_costs(current_date: datetime.date, direct_debit: float, income: float, income_growth_percent: float, threshold: float, threshold_change_percent: float):
    total_personal = 0

    while current_date < expiry_date:
        current_date += datetime.timedelta(days=365//12)
        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

        total_personal += get_mandatory_payment(income, threshold) + direct_debit

        total_personal *= (1 + (0.05 / 12))  # Assuming a 5% annual return on investments

    return total_personal

def main():

    calc_loan_payed_off()

if "__main__" == __name__:
    main()