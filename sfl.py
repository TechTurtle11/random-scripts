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

def get_months_until_loan_payed_off(current_date: datetime.date, loan_value: float, income: float, direct_debit_percentage: float, threshold: float, annual_loan_interest_rate: float, income_growth_percent: float, threshold_change_percent: float):
    months = 0
    total_payed = 25000


    while loan_value > 0:
        months += 1
        current_date += datetime.timedelta(days=365//12)
        if current_date > expiry_date:
            print("Loan not payed off in 30 years, exiting.")
            return months, total_payed

        current_salary = take_home_pay(income, 5) # Assuming 5% pension contribution
        direct_debit = (direct_debit_percentage / 100) * current_salary / 12

        loan_value = month(loan_value, income, direct_debit, threshold, annual_loan_interest_rate)
        total_payed += get_mandatory_payment(income, threshold) + direct_debit

        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

    return months,total_payed


def calculate_investment_growth(current_date: datetime.date, income: float, monthly_contribution_percent: float, months: int, income_growth_percent: float) -> float:

    total_gained  = 0
    while months > 0:
        months -= 1
        current_date += datetime.timedelta(days=365//12)

        current_salary = take_home_pay(income, 5)  # Assuming 5% pension contribution

        monthly_contribution = (monthly_contribution_percent / 100) / 12 * current_salary

        total_gained += monthly_contribution

        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)

    return total_gained


def calculate_opportunity_costs(current_date: datetime.date, total_personal: float,income: float,  monthly_fixed_percentage: float, direct_debit_percentage: float, income_growth_percent: float, threshold: float, threshold_change_percent: float):

    while current_date < expiry_date:
        current_date += datetime.timedelta(days=365//12)
        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

        current_salary = take_home_pay(income, 5)  # Assuming 5% pension contribution
        direct_debit = (direct_debit_percentage / 100) * current_salary / 12
        monthly_fixed = (monthly_fixed_percentage / 100) * current_salary / 12

        total_personal += get_mandatory_payment(income, threshold) + monthly_fixed + direct_debit

        total_personal *= (1 + (0.05 / 12))  # Assuming a 5% annual return on investments

    return total_personal


def take_home_pay(income: float, pension_percent: float = 5) -> float:
    """
    Calculate UK take-home pay after Income Tax, National Insurance, and pension contributions (2023/24 rates).
    Assumes standard personal allowance and no student loan deductions.
    pension_percent: percentage of gross income contributed to pension (e.g., 5 for 5%)
    """
    # Deduct pension contributions from gross income
    pension_contrib = (pension_percent / 100) * income
    taxable_income_for_tax = income - pension_contrib

    # Income Tax bands (England, Wales, NI)
    personal_allowance = 12570
    basic_rate_limit = 50270
    higher_rate_limit = 125140

    # Income Tax calculation
    taxable_income = max(0, taxable_income_for_tax - personal_allowance)
    if taxable_income_for_tax <= personal_allowance:
        income_tax = 0
    elif taxable_income_for_tax <= basic_rate_limit:
        income_tax = taxable_income * 0.20
    elif taxable_income_for_tax <= higher_rate_limit:
        income_tax = (basic_rate_limit - personal_allowance) * 0.20 + (taxable_income_for_tax - basic_rate_limit) * 0.40
    else:
        # Personal allowance is reduced by £1 for every £2 over £100,000
        reduced_allowance = max(0, personal_allowance - ((taxable_income_for_tax - 100000) // 2))
        taxable_income = max(0, taxable_income_for_tax - reduced_allowance)
        income_tax = (basic_rate_limit - reduced_allowance) * 0.20
        income_tax += (higher_rate_limit - basic_rate_limit) * 0.40
        income_tax += (taxable_income_for_tax - higher_rate_limit) * 0.45

    # National Insurance (Class 1, employee, 2023/24)
    ni_free_allowance = 12570
    ni_upper_limit = 50270
    if income <= ni_free_allowance:
        ni = 0
    elif income <= ni_upper_limit:
        ni = (income - ni_free_allowance) * 0.08
    else:
        ni = (ni_upper_limit - ni_free_allowance) * 0.08 + (income - ni_upper_limit) * 0.02

    take_home = income - income_tax - ni - pension_contrib - (get_mandatory_payment(income,28470)*12)

    return take_home



def calc_loan_payed_off():

    start_date = datetime.datetime.now().date()

    loan_value = 43050.33
    income = 60000
    current_income = take_home_pay(income, 5)  # Assuming 5% pension contribution
    print(f"Take Home Pay: £{current_income:.2f} (after tax and pension contributions)")
    investment_percentage = (330 + 750 + 500) / (current_income/12) * 100
    direct_debit_percentage = (0) / (current_income/12) * 100
    threshold = 28470
    annual_loan_interest_rate = 7.3
    income_growth_percent = 3
    threshold_change_percent = 0

    print(f"Loan Value: £{loan_value:.2f}")
    print(f"Income: £{income:.2f} (growing at {income_growth_percent}% annually)")
    print(f"Direct Debit: £{(direct_debit_percentage/100)*(current_income/12):.2f}")
    print(f"Threshold: £{threshold:.2f} (growing at {threshold_change_percent}% annually)")
    print(f"Annual Loan Interest Rate: {annual_loan_interest_rate}%")
    print(f"Investment Per Month: £{(investment_percentage/100)*(current_income/12):.2f} (roi at an average rate of 5% annually)")
    print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    print("Calculating months until loan is paid off...")

    months,cost = get_months_until_loan_payed_off(start_date, loan_value, income, direct_debit_percentage, threshold, annual_loan_interest_rate, income_growth_percent, threshold_change_percent)
    years = months // 12
    remaining_months = months % 12
    date_payed_off = start_date + datetime.timedelta(days=months * 30)

    print(f"Loan will be paid off in {years} years and {remaining_months} months. Total cost: £{cost:.2f}")
    print(f"Expected date of loan payoff: {date_payed_off.strftime('%Y-%m-%d')}")


    investment_growth = calculate_investment_growth(start_date, income, investment_percentage, months, income_growth_percent)

    current_earned = investment_growth
    print(f"Total investment growth after loan payoff: £{investment_growth:.2f}")

    current_income = income * (1 + (income_growth_percent / 100)) ** (years + (remaining_months / 12))
    print(f"Current income after {years} years and {remaining_months} months: £{current_income:.2f}")

    after_30_years = calculate_opportunity_costs(date_payed_off, current_earned, current_income, investment_percentage, direct_debit_percentage, income_growth_percent, threshold, threshold_change_percent)

    print(f"Total gained after 30 years: £{after_30_years:.2f}")


def main():

    calc_loan_payed_off()

if "__main__" == __name__:
    main()