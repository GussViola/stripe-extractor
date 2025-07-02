import stripe
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv('STRIPE_API_KEY')


def get_customers_data():
    """Fetch all customers from Stripe API"""
    customers = []

    # Pagination to get all customers
    has_more = True
    starting_after = None

    while has_more:
        params = {"limit": 100}
        if starting_after:
            params["starting_after"] = starting_after

        # Get customer data with subscriptions expanded
        response = stripe.Customer.list(
            **params, expand=["data.subscriptions"])

        customers.extend(response.data)
        has_more = response.has_more
        if has_more:
            starting_after = response.data[-1].id

    return customers


def extract_customer_info(customers):
    """Extract required information from customers"""
    customer_data = []

    for customer in customers:
        # Get basic customer info
        name = customer.name if customer.name else "Vazio"
        email = customer.email if customer.email else "Vazio"
        phone = customer.phone if customer.phone else "Vazio"

        # Get active subscriptions
        active_subscriptions = []
        if hasattr(customer, 'subscriptions') and customer.subscriptions:
            for sub in customer.subscriptions.data:
                if sub.status == 'active':
                    # Access items data directly if available
                    if hasattr(sub, 'items') and hasattr(sub.items, 'data') and sub.items.data:
                        item = sub.items.data[0]
                        if hasattr(item, 'plan'):
                            plan = item.plan
                            plan_name = plan.nickname if hasattr(
                                plan, 'nickname') and plan.nickname else plan.id
                            active_subscriptions.append(plan_name)
                    else:
                        if hasattr(sub, 'plan') and hasattr(sub.plan, 'nickname'):
                            active_subscriptions.append(f"{sub.plan.nickname}")
                        else:
                            active_subscriptions.append(
                                f"Subscription ID: {sub.id} (Plan details unavailable)")
        subscription_string = ", ".join(
            active_subscriptions) if active_subscriptions else "Vazio"

        customer_data.append({
            'name': name,
            'email': email,
            'phone': phone,
            'active_subscriptions': subscription_string,
        })

    return customer_data


def save_to_csv(customer_data, output_file=None):
    """Save customer data to CSV file"""
    if not output_file:
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        output_file = os.path.join(
            'outputs', f'stripe_customers_{timestamp}.csv')

    os.makedirs('outputs', exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'email', 'phone', 'active_subscriptions']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for customer in customer_data:
            writer.writerow(customer)

    return output_file


def main():
    print("Fetching customer data from Stripe...")
    customers = get_customers_data()
    print(f"Found {len(customers)} customers.")

    print("Extracting customer information...")
    customer_data = extract_customer_info(customers)

    print("Saving data to CSV...")
    output_file = save_to_csv(customer_data)

    print(f"Done! Customer data saved to {output_file}")


if __name__ == "__main__":
    # You can set your API key as an environment variable before running
    # or replace the api_key value in the script
    if not stripe.api_key:
        api_key = os.environ.get('STRIPE_API_KEY')
        if not api_key:
            stripe.api_key = input("Please enter your Stripe API key: ")
        else:
            stripe.api_key = api_key

    main()
