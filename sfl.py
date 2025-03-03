




def next_month_value(prev, income, loan_rate, monthly_payment, threshold):

    if income < 28000:
        mandatory_payment = 0
    else:
        mandatory_payment = get_mandatory_payment(income,threshold)/12

    if prev > 0:
        prev = prev * (1 + ((loan_rate / 12)/100) )


    prev = prev - mandatory_payment - monthly_payment

    return prev


def get_mandatory_payment(annual_income, threshold, percentage = 9):
    affected_amount = annual_income - threshold
    return (percentage/100) * affected_amount


def main():

    loan_value = 45000
    months_paying = 0

    income = 60000
    income_growth_percent = 3

    threshold = 27295
    threshold_change_percent = 2


    interest_rate = 7.3

    monthly_payment = 750
    other_investments_monthly = 500

    total_personal = 0
    loan_payed_off_accepted = False

    print(f"{loan_value=} {income=} {income_growth_percent=} {threshold=} {threshold_change_percent=} {interest_rate=} {monthly_payment=}")
    while months_paying < 28*12:


        if loan_value > 0:
            loan_value = next_month_value(loan_value,income,interest_rate,monthly_payment,threshold)
        else:
            loan_value = 0

        if loan_value <= 0 and not loan_payed_off_accepted:
                print(f"loan payed off after {months_paying/12} years")
                loan_payed_off_accepted = True


        if loan_value <= 0:
            total_personal += (get_mandatory_payment(income,threshold) / 12) + monthly_payment

        total_personal += other_investments_monthly
        total_personal = total_personal *  (1+(0.05 / 12))

        if months_paying % 12 == 0:
            income = income * (1 + (income_growth_percent / 100))
            threshold = threshold * (1 + (threshold_change_percent / 100))

        #print(f"Current Time: {months_paying//12}y {months_paying%12}m current loan value {loan_value}")

        months_paying+=1

    print(f"after {months_paying/12} years")
    print(f"total personal {total_personal}")



if "__main__" == __name__:
    main()