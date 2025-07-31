import datetime


START_DATE = datetime.date(2023, 5, 22)  # date repayments started
EXPIRY_DATE = START_DATE + datetime.timedelta(days=365 * 30)  # 30 years from start date


def take_home_pay(income: float, pension_percent: float = 5, student_finance_threshold: float = 28470) -> float:
    """
    Calculate UK take-home pay after tax, NI, pension, and student loan deductions.

    Parameters:
        income (float): Gross annual income.
        pension_percent (float): Percentage of income contributed to pension.
        student_finance_threshold (float): Income threshold for student loan repayments.

    Returns:
        float: Annual take-home pay after deductions.
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

    take_home = income - income_tax - ni - pension_contrib - (get_mandatory_payment(income, student_finance_threshold) * 12)

    return take_home


def get_mandatory_payment(income, threshold, percentage=9) -> float:
    """
    Calculate monthly mandatory student loan payment based on income and threshold.

    Parameters:
        income (float): Gross annual income.
        threshold (float): Repayment threshold for student loan.
        percentage (float): Repayment rate as a percentage of income above threshold.

    Returns:
        float: Monthly mandatory payment.
    """
    affected_amount = (income - threshold) / 12
    return (percentage / 100) * affected_amount


def update_annual(income: float, annual_growth_percent: float) -> float:
    """
    Update a value by an annual growth percentage.

    Parameters:
        income (float): Current value.
        annual_growth_percent (float): Annual growth rate in percent.

    Returns:
        float: Updated value after growth.
    """
    return income * (1 + (annual_growth_percent / 100))


def month(
    loan_value: float, income: float, direct_debit: float, threshold: float, annual_loan_interest_rate: float
) -> float:
    """
    Calculate new loan value after one month, accounting for interest and repayments.

    Parameters:
        loan_value (float): Current loan balance.
        income (float): Gross annual income.
        direct_debit (float): Monthly direct debit payment.
        threshold (float): Student loan repayment threshold.
        annual_loan_interest_rate (float): Annual interest rate on the loan.

    Returns:
        float: Updated loan balance after one month.
    """
    mandatory = get_mandatory_payment(income, threshold)

    interest = ((annual_loan_interest_rate / 100) / 12) * loan_value
    loan_value += interest
    new_loan = loan_value - mandatory - direct_debit

    return new_loan


def get_months_until_loan_payed_off(
    current_date: datetime.date,
    loan_value: float,
    income: float,
    direct_debit_percentage: float,
    threshold: float,
    annual_loan_interest_rate: float,
    income_growth_percent: float,
    threshold_change_percent: float,
) -> tuple[int, float]:
    """
    Simulate months until loan is paid off, considering salary growth and repayments.

    Parameters:
        current_date (datetime.date): Start date of simulation.
        loan_value (float): Initial loan balance.
        income (float): Initial gross annual income.
        direct_debit_percentage (float): Direct debit as a percent of take-home pay.
        threshold (float): Student loan repayment threshold.
        annual_loan_interest_rate (float): Annual interest rate on the loan.
        income_growth_percent (float): Annual income growth rate.
        threshold_change_percent (float): Annual threshold growth rate.

    Returns:
        tuple[int, float]: (Months until payoff, total paid)
    """
    months = 0
    total_payed = 25000

    while loan_value > 0:
        months += 1
        current_date += datetime.timedelta(days=365 // 12)
        if current_date > EXPIRY_DATE:
            print("Loan not payed off in 30 years, exiting.")
            return months, total_payed

        current_salary = take_home_pay(income, 5, threshold)  # Assuming 5% pension contribution
        direct_debit = (direct_debit_percentage / 100) * current_salary / 12

        loan_value = month(loan_value, income, direct_debit, threshold, annual_loan_interest_rate)
        total_payed += get_mandatory_payment(income, threshold) + direct_debit

        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

    return months, total_payed


def calculate_investment_growth(
    current_date: datetime.date,
    income: float,
    monthly_contribution_percent: float,
    months: int,
    income_growth_percent: float,
    threshold: float,
    threshold_change_percent: float,
) -> float:
    """
    Calculate total investment growth over a period, with salary and threshold changes.

    Parameters:
        current_date (datetime.date): Start date of simulation.
        income (float): Initial gross annual income.
        monthly_contribution_percent (float): Percent of take-home pay invested monthly.
        months (int): Number of months to simulate.
        income_growth_percent (float): Annual income growth rate.
        threshold (float): Student loan repayment threshold.
        threshold_change_percent (float): Annual threshold growth rate.

    Returns:
        float: Total invested amount after the period.
    """
    total_gained = 0
    while months > 0:
        months -= 1
        current_date += datetime.timedelta(days=365 // 12)

        current_salary = take_home_pay(income, 5, threshold)  # Assuming 5% pension contribution

        monthly_contribution = (monthly_contribution_percent / 100) / 12 * current_salary

        total_gained += monthly_contribution

        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

    return total_gained


def calculate_assets_after_expiry(
    current_date: datetime.date,
    total_personal: float,
    income: float,
    monthly_fixed_percentage: float,
    direct_debit_percentage: float,
    income_growth_percent: float,
    threshold: float,
    threshold_change_percent: float,
) -> float:
    """
    Calculate total assets after expiry date, considering investments and repayments.

    Parameters:
        current_date (datetime.date): Start date of simulation.
        total_personal (float): Initial asset value.
        income (float): Initial gross annual income.
        monthly_fixed_percentage (float): Fixed investment as percent of take-home pay.
        direct_debit_percentage (float): Direct debit as percent of take-home pay.
        income_growth_percent (float): Annual income growth rate.
        threshold (float): Student loan repayment threshold.
        threshold_change_percent (float): Annual threshold growth rate.

    Returns:
        float: Total assets at expiry date.
    """
    while current_date < EXPIRY_DATE:
        current_date += datetime.timedelta(days=365 // 12)
        if current_date.month == 4:
            income = update_annual(income, income_growth_percent)
            threshold = update_annual(threshold, threshold_change_percent)

        current_salary = take_home_pay(income, 5)  # Assuming 5% pension contribution
        direct_debit = (direct_debit_percentage / 100) * current_salary / 12
        monthly_fixed = (monthly_fixed_percentage / 100) * current_salary / 12

        total_personal += get_mandatory_payment(income, threshold) + monthly_fixed + direct_debit

        total_personal *= 1 + (0.05 / 12)  # Assuming a 5% annual return on investments

    return total_personal


def calc_loan_payed_off():
    """
    Main routine: prints loan payoff timeline, investment growth, and total assets after 30 years.

    Parameters:
        None

    Returns:
        None
    """
    current_date = datetime.datetime.now().date()

    loan_value = 43050.33
    income = 80000
    threshold = 28470
    current_income = take_home_pay(
        income, pension_percent=5, student_finance_threshold=threshold
    )  # Assuming 5% pension contribution
    print(f"Take Home Pay: £{current_income:.2f} (after tax and pension contributions)")
    investment_percentage = (330 + 750 + 250) / (current_income / 12) * 100
    direct_debit_percentage = (750) / (current_income / 12) * 100
    annual_loan_interest_rate = 7.3
    income_growth_percent = 3
    threshold_change_percent = 3

    print(f"Loan Value: £{loan_value:.2f}")
    print(f"Income: £{income:.2f} (growing at {income_growth_percent}% annually)")
    print(f"Direct Debit: £{(direct_debit_percentage / 100) * (current_income / 12):.2f}")
    print(f"Threshold: £{threshold:.2f} (growing at {threshold_change_percent}% annually)")
    print(f"Annual Loan Interest Rate: {annual_loan_interest_rate}%")
    print(
        f"Investment Per Month: £{(investment_percentage / 100) * (current_income / 12):.2f} (roi at an average rate of 5% annually)"
    )
    print(f"Start Date: {current_date.strftime('%Y-%m-%d')}")
    print("Calculating months until loan is paid off...")

    months_until_payoff, cost = get_months_until_loan_payed_off(
        current_date,
        loan_value,
        income,
        direct_debit_percentage,
        threshold,
        annual_loan_interest_rate,
        income_growth_percent,
        threshold_change_percent,
    )
    years = months_until_payoff // 12
    remaining_months = months_until_payoff % 12
    date_payed_off = current_date + datetime.timedelta(days=months_until_payoff * 30)

    investments_after_payed_off = calculate_investment_growth(
        current_date,
        income,
        investment_percentage,
        months_until_payoff,
        income_growth_percent,
        threshold,
        threshold_change_percent,
    )

    print(f"Expected date of loan payoff: {date_payed_off.strftime('%Y-%m-%d')}")
    print(f"Loan will be paid off in {years} years and {remaining_months} months. Total cost: £{cost:.2f}")
    print(f"Total investments after loan payoff: £{investments_after_payed_off:.2f}")

    current_earned = investments_after_payed_off
    current_income = income * (1 + (income_growth_percent / 100)) ** (months_until_payoff / 12)
    current_threshold = threshold * (1 + (threshold_change_percent / 100)) ** (months_until_payoff / 12)
    print(f"Estimated income after {years} years and {remaining_months} months: £{current_income:.2f}")

    after_30_years = calculate_assets_after_expiry(
        date_payed_off,
        current_earned,
        current_income,
        investment_percentage,
        direct_debit_percentage,
        income_growth_percent,
        current_threshold,
        threshold_change_percent,
    )

    print(f"Total assets after 30 years: £{after_30_years:.2f}")


if "__main__" == __name__:
    calc_loan_payed_off()
