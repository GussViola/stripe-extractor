import stripe
import csv
import os
import sys
from datetime import datetime
import time
from dotenv import load_dotenv

load_dotenv()

# Carregamos a chave API mas ainda não validamos


def get_customers_data():
    """Fetch all customers from Stripe API"""
    customers = []

    # Pagination to get all customers
    has_more = True
    starting_after = None

    try:
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

    except stripe.error.AuthenticationError:
        print(
            "\nErro de autenticação: A chave API do Stripe é inválida ou não foi fornecida.")
        new_key = input("\nPor favor, digite sua chave API do Stripe: ")
        if new_key.strip():
            stripe.api_key = new_key
            # Salvar a nova chave no arquivo .env
            with open('.env', 'w') as env_file:
                env_file.write(f"STRIPE_API_KEY={new_key}")
            print("Chave API salva no arquivo .env. Tentando novamente...\n")
            # Tentar novamente com a nova chave
            return get_customers_data()
        else:
            print("Nenhuma chave API fornecida. Encerrando.")
            sys.exit(1)
    except Exception as e:
        print(f"\nErro ao buscar dados: {str(e)}")
        sys.exit(1)

    return customers


def extract_customer_info(customers):
    """Extract required information from customers"""
    customer_data = []

    for customer in customers:
        # Get basic customer info
        name = customer.name if customer.name else "Vazio"
        email = customer.email if customer.email else "Vazio"
        phone = customer.phone if customer.phone else "Vazio"

        # Converter timestamp de criação da conta para data legível
        created_timestamp = customer.created
        created_date = datetime.fromtimestamp(created_timestamp).strftime(
            '%d/%m/%Y') if created_timestamp else "Vazio"

        # Get active subscriptions and their start dates
        active_subscriptions = []
        subscription_dates = []

        if hasattr(customer, 'subscriptions') and customer.subscriptions:
            for sub in customer.subscriptions.data:
                if sub.status == 'active':
                    # Get subscription start date
                    start_date = ""
                    if hasattr(sub, 'start_date') and sub.start_date:
                        start_timestamp = sub.start_date
                        start_date = datetime.fromtimestamp(
                            start_timestamp).strftime('%d/%m/%Y')

                    # Access items data directly if available
                    if hasattr(sub, 'items') and hasattr(sub.items, 'data') and sub.items.data:
                        item = sub.items.data[0]
                        if hasattr(item, 'plan'):
                            plan = item.plan
                            plan_name = plan.nickname if hasattr(
                                plan, 'nickname') and plan.nickname else plan.id
                            active_subscriptions.append(plan_name)
                            subscription_dates.append(start_date)
                    else:
                        if hasattr(sub, 'plan') and hasattr(sub.plan, 'nickname'):
                            active_subscriptions.append(f"{sub.plan.nickname}")
                            subscription_dates.append(start_date)
                        else:
                            active_subscriptions.append(
                                f"Subscription ID: {sub.id} (Plan details unavailable)")
                            subscription_dates.append(start_date)
        # Prepare subscription strings
        subscription_string = ", ".join(
            active_subscriptions) if active_subscriptions else "Free"

        # Prepare subscription dates string
        subscription_dates_string = ", ".join(
            [date for date in subscription_dates if date]) if subscription_dates else ""
        if subscription_string == "Free":
            subscription_dates_string = ""

        customer_data.append({
            'Nome': name,
            'Email': email,
            'Telefone': phone,
            'Data de Criação': created_date,
            'Data de Assinatura': subscription_dates_string,
            'Assinaturas Ativas': subscription_string,
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
        fieldnames = ['Nome', 'Email', 'Telefone', 'Data de Criação',
                      'Data de Assinatura', 'Assinaturas Ativas']
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
    # Verificar se temos uma chave API
    api_key = os.environ.get('STRIPE_API_KEY')
    if not api_key:
        stripe.api_key = input("Por favor, digite sua chave API do Stripe: ")
        # Salvar a chave no arquivo .env para uso futuro
        if stripe.api_key:
            with open('.env', 'w') as env_file:
                env_file.write(f"STRIPE_API_KEY={stripe.api_key}")
    else:
        stripe.api_key = api_key

    # Mesmo se tivermos uma chave do arquivo .env, ela pode ser inválida
    # O método get_customers_data() vai lidar com erros de autenticação

    main()
