from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime
from datetime import timedelta
from .models import Customer, Loan
from rest_framework.decorators import api_view
from decimal import Decimal



@api_view(['POST'])
def register_customer(request):
    # Get data from request body
    if request.method == 'POST':
        data = request.data

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        age = data.get('age')
        monthly_income = data.get('monthly_income')
        phone_number = data.get('phone_number')
        
        # Validate data (you can add more validation as needed)
        if not (first_name and last_name and age and monthly_income and phone_number):
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        try:
            age = int(age)
            monthly_income = int(monthly_income)
            phone_number = int(phone_number)
        except ValueError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)
        
        # Calculate approved credit limit
        approved_limit = round(36 * monthly_income, -5)  # Round to nearest lakh
        
        # Create new customer
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=age,
            monthly_salary=monthly_income,
            approved_limit=approved_limit,
            phone_number=phone_number
        )
        
        # Return response with customer details
        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }
        return JsonResponse(response_data, status=201)




def calculate_credit_score(customer_id):
    # Retrieve customer and loan data
    customer = Customer.objects.get(customer_id=customer_id)
    loans = Loan.objects.filter(customer_id=customer_id)
    
    # Calculate components for credit score
    paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
    num_loans = loans.count()
    current_year = datetime.now().year
    current_year_loans = loans.filter(start_date__year=current_year)
    loan_activity = current_year_loans.count()
    loan_approved_volume = sum(loan.loan_amount for loan in loans)
    sum_current_loans = sum(loan.monthly_repayment for loan in loans)
    
    # Calculate credit score components
    credit_score = (paid_on_time / num_loans) * 30
    credit_score += (loan_activity / num_loans) * 20
    score = Decimal(credit_score)
    credit_score = score + (loan_approved_volume / customer.approved_limit) * 30
    if sum_current_loans > customer.approved_limit:
        credit_score = 0
    
    return credit_score


@api_view(['POST'])
def check_eligibility(request):
    # Get data from request body
    if request.method == 'POST':
        data = request.data
        if not (data.get('customer_id') and data.get('loan_amount') and data.get('interest_rate') and data.get('tenure')):
            return JsonResponse({'error': 'Fields are missing'}, status=400)
        customer_id = data.get('customer_id')
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))
        
        # Calculate credit score
        credit_score = calculate_credit_score(customer_id)
        
        # Check loan eligibility based on credit score
        if credit_score > 50:
            loan_approved = True
        elif 30 < credit_score <= 50:
            if interest_rate <= 12:
                interest_rate = 12
        elif 10 < credit_score <= 30:
            if interest_rate <= 16:
                interest_rate = 16
        else:
            loan_approved = False
        
        # Check if sum of all current EMIs > 50% of monthly salary
        monthly_salary = Customer.objects.get(customer_id=customer_id).monthly_salary
        sum_current_emis = sum(loan.monthly_repayment for loan in Loan.objects.filter(customer_id=customer_id))
        if sum_current_emis > Decimal(0.5) * monthly_salary:
            loan_approved = False
        
        # Determine monthly installment
        monthly_installment = loan_amount * ((interest_rate / 100) / 12) / (1 - (1 + ((interest_rate / 100) / 12)) ** -tenure)
        
        # Return response
        response_data = {
            'customer_id': customer_id,
            'approval': loan_approved,
            'interest_rate': interest_rate,
            'corrected_interest_rate': interest_rate,  # Placeholder for corrected interest rate
            'tenure': tenure,
            'monthly_installment': monthly_installment
        }
        return JsonResponse(response_data)






def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_installment = loan_amount * ((interest_rate / 100) / 12) / (1 - (1 + ((interest_rate / 100) / 12)) ** -tenure)
    return monthly_installment


@api_view(['POST'])
def create_loan(request):

    if request.method == 'POST':
        data = request.data

        if not (data.get('customer_id') and data.get('loan_amount') and data.get('interest_rate') and data.get('tenure')):
            return JsonResponse({'error': 'Fields are missing'}, status=400)
        print("data", data)
        # Get data from request body
        customer_id = data.get('customer_id')
        print("loan_amount", data.get('loan_amount'))
        loan_amount = float(data.get('loan_amount'))
        interest_rate = float(data.get('interest_rate'))
        tenure = int(data.get('tenure'))
        
        # Check eligibility (you can call the check_eligibility function or implement eligibility check here)
        # For simplicity, let's assume eligibility is checked here
        # You may call the /check-eligibility endpoint for a more modular approach
        # and to reuse the eligibility logic
        eligible = True  # Assuming the customer is eligible
        
        # Process loan
        if eligible:
            # Create new loan object
            loan = Loan.objects.create(
                customer_id=customer_id,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                tenure=tenure,
                monthly_repayment=calculate_monthly_installment(loan_amount, interest_rate, tenure),
                start_date=datetime.now(),

                # Calculate the end date based on the tenure (number of months)
                end_date = datetime.now() + timedelta(days=30 * tenure)  # Assuming each month has 30 days
                ,
                emis_paid_on_time=0  # Assuming no EMIs paid on time initially
            )
            # Return response with loan details
            response_data = {
                'loan_id': loan.id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved',
                'monthly_installment': loan.monthly_repayment
            }
        else:
            # Return response indicating loan not approved
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan not approved due to eligibility criteria',
                'monthly_installment': None
            }
        
        return JsonResponse(response_data)



@api_view(['GET'])
def view_loan_details(request, loan_id):
    try:
        # Retrieve loan object
        loan = Loan.objects.get(id=loan_id)
        
        # Retrieve customer details
        customer = {
            'id': loan.customer.customer_id,
            'first_name': loan.customer.first_name,
            'last_name': loan.customer.last_name,
            'phone_number': loan.customer.phone_number,
            'age': loan.customer.age
        }
        
        # Prepare response data
        response_data = {
            'loan_id': loan.id,
            'customer': customer,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_repayment,
            'tenure': loan.tenure
        }

        print(response_data)
        
        return JsonResponse(response_data)
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'Loan not found'}, status=404)




@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        # Retrieve all current loans associated with the customer ID
        loans = Loan.objects.filter(customer_id=customer_id)
        
        # Prepare response data
        loan_details = []
        for loan in loans:
            loan_item = {
                'loan_id': loan.id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'repayments_left': loan.tenure - loan.emis_paid_on_time
            }
            loan_details.append(loan_item)
        
        return JsonResponse(loan_details, safe=False)  # safe=False allows serialization of lists
    except Loan.DoesNotExist:
        return JsonResponse({'error': 'No loans found for the specified customer ID'}, status=404)
