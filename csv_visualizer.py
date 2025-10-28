import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Default CSV path (can override with command line argument)
csv_path = sys.argv[1] if len(sys.argv) > 1 else "report1761596138289.csv"

if not os.path.exists(csv_path):
    print(f"File not found: {csv_path}")
    sys.exit(1)

# Read CSV
df = pd.read_csv(csv_path)

# Clean column names
df.columns = [col.strip().replace(" ", "_").replace(":", "") for col in df.columns]

# Convert Total to numeric (remove commas, convert to float)
df['Total'] = pd.to_numeric(df['Total'].astype(str).str.replace(',', ''), errors='coerce')

# Convert Invoice_Date to datetime
df['Invoice_Date'] = pd.to_datetime(df['Invoice_Date'], errors='coerce')

# --- Dynamic Visualizations ---
def spend_by_account():
    plt.figure(figsize=(10,6))
    tmp = df.groupby('Account_Name')['Total'].sum().sort_values(ascending=False)
    tmp.plot(kind='bar')
    plt.title('Total Spend by Account')
    plt.ylabel('Total Spend (USD)')
    plt.xlabel('Account Name')
    plt.tight_layout()
    plt.show()
    export = input("Export this chart as PNG/PDF? (y/n): ").strip().lower()
    if export == 'y':
        fname = input("Enter filename (without extension): ").strip() or 'spend_by_account'
        plt.savefig(f"{fname}.png")
        plt.savefig(f"{fname}.pdf")
        print(f"Saved as {fname}.png and {fname}.pdf")
    plt.close()

def spend_by_product():
    plt.figure(figsize=(12,6))
    tmp = df.groupby('Product_Product_Name')['Total'].sum().sort_values(ascending=False).head(20)
    tmp.plot(kind='bar')
    plt.title('Total Spend by Product (Top 20)')
    plt.ylabel('Total Spend (USD)')
    plt.xlabel('Product Name')
    plt.tight_layout()
    plt.show()
    export = input("Export this chart as PNG/PDF? (y/n): ").strip().lower()
    if export == 'y':
        fname = input("Enter filename (without extension): ").strip() or 'spend_by_product'
        plt.savefig(f"{fname}.png")
        plt.savefig(f"{fname}.pdf")
        print(f"Saved as {fname}.png and {fname}.pdf")
    plt.close()

def spend_by_pricebook():
    plt.figure(figsize=(12,6))
    tmp = df.groupby('Price_Book_Price_Book_Name')['Total'].sum().sort_values(ascending=False)
    tmp.plot(kind='bar')
    plt.title('Total Spend by Price Book')
    plt.ylabel('Total Spend (USD)')
    plt.xlabel('Price Book Name')
    plt.tight_layout()
    plt.show()
    export = input("Export this chart as PNG/PDF? (y/n): ").strip().lower()
    if export == 'y':
        fname = input("Enter filename (without extension): ").strip() or 'spend_by_pricebook'
        plt.savefig(f"{fname}.png")
        plt.savefig(f"{fname}.pdf")
        print(f"Saved as {fname}.png and {fname}.pdf")
    plt.close()

def month_over_month_by_account_and_pricebook():
    # Pivot table: index = Month, columns = Account, values = sum of Total, grouped by Price Book
    df['Month'] = df['Invoice_Date'].dt.to_period('M')
    pivot = df.pivot_table(index='Month', columns=['Account_Name', 'Price_Book_Price_Book_Name'], values='Total', aggfunc='sum', fill_value=0)
    # Plot for each account, summarized by price book
    for account in df['Account_Name'].unique():
        plt.figure(figsize=(14,7))
        sub = pivot[account]
        sub.plot(kind='bar', stacked=True)
        plt.title(f"Month-over-Month Spend for {account} (by Price Book)")
        plt.ylabel('Total Spend (USD)')
        plt.xlabel('Month')
        plt.legend(title='Price Book', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()
        export = input(f"Export this chart for {account} as PNG/PDF? (y/n): ").strip().lower()
        if export == 'y':
            fname = input("Enter filename (without extension): ").strip() or f'monthly_spend_{account.replace(" ", "_")}'
            plt.savefig(f"{fname}.png")
            plt.savefig(f"{fname}.pdf")
            print(f"Saved as {fname}.png and {fname}.pdf")
        plt.close()

def ytd_summary(year=None):
    # Filter for current year if not specified
    if year is None:
        year = pd.Timestamp.now().year
    ytd = df[df['Invoice_Date'].dt.year == year]
    summary = ytd.groupby(['Account_Name', 'Price_Book_Price_Book_Name'])['Total'].sum().unstack(fill_value=0)
    print(f"\nYTD Spend Summary ({year}):")
    print(summary.round(2))
    return summary

def dynamic_menu():
    while True:
        print("\nAvailable visualizations:")
        print("1. Total Spend by Account")
        print("2. Total Spend by Product (Top 20)")
        print("3. Total Spend by Price Book")
        print("4. Month-over-Month Spend by Account (by Price Book)")
        print("5. YTD Spend Summary Table")
        print("0. Exit")
        choice = input("\nChoose a visualization (0-5): ")
        if choice == '1':
            spend_by_account()
        elif choice == '2':
            spend_by_product()
        elif choice == '3':
            spend_by_pricebook()
        elif choice == '4':
            month_over_month_by_account_and_pricebook()
        elif choice == '5':
            ytd_summary()
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please enter a number between 0 and 5.")

if __name__ == "__main__":
    dynamic_menu()

