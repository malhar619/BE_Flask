from flask import Flask, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

def generate_plots(file_name):
    df = pd.read_csv(file_name, thousands=',')

    df['BID QTY'] = pd.to_numeric(df['BID QTY'], errors='coerce')
    df['C BID QTY'] = pd.to_numeric(df['C BID QTY'], errors='coerce')
    df['OI'] = pd.to_numeric(df['OI'], errors='coerce')
    df['C OI'] = pd.to_numeric(df['C OI'], errors='coerce')

    put_call_ratio = df['BID QTY'][10:-10].sum() / df['C BID QTY'][10:-10].sum()
    put_oi_call_oi_ratio = df['OI'][10:-10].sum() / df['C OI'][10:-10].sum()

    return {
        'put_call_ratio': float(put_call_ratio),
        'put_oi_call_oi_ratio': float(put_oi_call_oi_ratio),
    }

def generate_plot(file_name, plot_name):
    df = pd.read_csv(file_name, thousands=',')

    if plot_name == 'oi':
        plot_title = 'C OI vs OI'
        x_data = df['C OI'][50:-10]
        y_data = df['OI'][50:-10]
    elif plot_name == 'volume':
        plot_title = 'C VOLUME vs VOLUME'
        x_data = df['C VOLUME'][50:-10]
        y_data = df['VOLUME'][50:-10]
    else:
        return None

    plt.figure(figsize=(12, 6))
    plt.plot(x_data, y_data, marker='o', linestyle='-', color='b')
    plt.title(plot_title)
    plt.xlabel('X-axis Label')
    plt.ylabel('Y-axis Label')
    plt.grid(True)

    plot_path = f'plots/{plot_name}_plot.png'
    plt.savefig(plot_path)
    plt.close()

    return plot_path





@app.route('/get_nifty_plots')
def get_nifty_plots():
    nifty_plots_data = generate_plots('nifty.csv')
    return jsonify(nifty_plots_data)

@app.route('/get_banknifty_plots')
def get_banknifty_plots():
    banknifty_plots_data = generate_plots('banknifty.csv')
    return jsonify(banknifty_plots_data)

# New route for finnifty.csv
@app.route('/get_finnifty_plots')
def get_finnifty_plots():
    finnifty_plots_data = generate_plots('finnifty.csv')
    return jsonify(finnifty_plots_data)




@app.route('/get_nifty_plot/<plot_name>')
def get_nifty_plot(plot_name):
    plot_path = generate_plot('nifty.csv', plot_name)
    if plot_path:
        return send_file(plot_path, mimetype='image/png')
    else:
        return 'Invalid plot name', 400

@app.route('/get_banknifty_plot/<plot_name>')
def get_banknifty_plot(plot_name):
    plot_path = generate_plot('banknifty.csv', plot_name)
    if plot_path:
        return send_file(plot_path, mimetype='image/png')
    else:
        return 'Invalid plot name', 400

# New route for finnifty.csv
@app.route('/get_finnifty_plot/<plot_name>')
def get_finnifty_plot(plot_name):
    plot_path = generate_plot('finnifty.csv', plot_name)
    if plot_path:
        return send_file(plot_path, mimetype='image/png')
    else:
        return 'Invalid plot name', 400


#######################################################################################################
@app.route('/small_cap_data')
def index():
    # Sample data (replace this with your actual data)
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html')[0]

    # Convert '1Y' column to numeric after removing '%' symbol
    data['1Y'] = pd.to_numeric(data['1Y'].str.rstrip('%'), errors='coerce')

    # Convert '1Y' column to numeric after removing '%' symbol
    data['3Y'] = pd.to_numeric(data['3Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with 'NaN' in the '1Y' column
    data = data.dropna(subset=['1Y'])

    # Drop rows with 'NaN' in the '1Y' column
    data = data.dropna(subset=['3Y'])

    # Drop duplicate entries based on 'Scheme Name'
    data = data.drop_duplicates(subset=['Scheme Name'], keep='first')

    # Convert the data to JSON
    json_data = data.to_dict(orient='records')

    # Return JSON response
    return jsonify(json_data)



def recommend_top_mutual_funds_1Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html')[0]

    # Convert '1Y' column to numeric after removing '%' symbol
    data['1Y'] = pd.to_numeric(data['1Y'].str.rstrip('%'), errors='coerce')


#   # Replace NaN values with a placeholder (e.g., -1)
#     data['1Y'].fillna(-1, inplace=True)
    # Drop rows with NaN values in the '1Y' column
    data.dropna(subset=['1Y'], inplace=True)


    #drop all the rows from the dataset where AUM values is zero
    data = data[data['AuM (Cr)'] != 0]


    # Sort the DataFrame based on '1Y' in descending order
    sorted_data = data.sort_values(by='1Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '1Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_small_cap_mutual_funds_1Y', methods=['GET'])
def get_top_mutual_funds():
    # Get parameters from the request if needed
    # For example, you can use request.args.get('top_n', type=int, default=10) to get the 'top_n' parameter

    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_1Y()

    # Return the top mutual funds as a JSON response
    return jsonify({'top_mutual_funds': top_mutual_funds})



def recommend_top_mutual_funds_3Y(top_n=65):
    #  URL to fetch real timedata 
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html')[0]

    # Convert '3Y' column to numeric after removing '%' symbol
    data['3Y'] = pd.to_numeric(data['3Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with NaN values in the '3Y' column
    data.dropna(subset=['3Y'], inplace=True)

    # Sort the DataFrame based on '3Y' in descending order
    sorted_data = data.sort_values(by='3Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '3Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict


@app.route('/get_small_cap_mutual_funds_3Y', methods=['GET'])
def get_top_mutual_funds_3Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_3Y()

    # Return the top mutual funds as a JSON response with '3Y' key
    return jsonify({'top_mutual_funds_3Y': top_mutual_funds})





# SMALL CAP FUNDS 5 YEAR RETURNS
def recommend_top_mutual_funds_5Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html')[0]

    # Convert '5Y' column to numeric after removing '%' symbol
    data['5Y'] = pd.to_numeric(data['5Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with NaN values in the '5Y' column
    data.dropna(subset=['5Y'], inplace=True)

    # Sort the DataFrame based on '5Y' in descending order
    sorted_data = data.sort_values(by='5Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '5Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_small_cap_mutual_funds_5Y', methods=['GET'])
def get_top_mutual_funds_5Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_5Y()

    # Return the top mutual funds as a JSON response with '5Y' key
    return jsonify({'top_mutual_funds_5Y': top_mutual_funds})


# SMALL CAP FUNDS 10 YEAR RETURNS
def recommend_top_mutual_funds_10Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/small-cap-fund.html')[0]

    # Convert '10Y' column to numeric after removing '%' symbol
    data['10Y'] = pd.to_numeric(data['10Y'].str.rstrip('%'), errors='coerce')

    # data['10Y'].fillna(-1, inplace=True)


    # Drop rows with NaN values in the '10Y' column
    data.dropna(subset=['10Y'], inplace=True)


    # Sort the DataFrame based on '10Y' in descending order
    sorted_data = data.sort_values(by='10Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '10Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_small_cap_mutual_funds_10Y', methods=['GET'])
def get_top_mutual_funds_10Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_10Y()

    # Return the top mutual funds as a JSON response with '10Y' key
    return jsonify({'top_mutual_funds_10Y': top_mutual_funds})



############################################################################  MID CAP FUNDS ENDPOINTS ###################################################################################



@app.route('/mid_cap_data')
def index_mid_cap():
    # Sample data (replace this with your actual data)
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '1Y' column to numeric after removing '%' symbol
    data['1Y'] = pd.to_numeric(data['1Y'].str.rstrip('%'), errors='coerce')

    # Convert '1Y' column to numeric after removing '%' symbol
    data['3Y'] = pd.to_numeric(data['3Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with 'NaN' in the '1Y' column
    data = data.dropna(subset=['1Y'])

    # Drop rows with 'NaN' in the '1Y' column
    data = data.dropna(subset=['3Y'])

    # Drop duplicate entries based on 'Scheme Name'
    data = data.drop_duplicates(subset=['Scheme Name'], keep='first')

    # Convert the data to JSON
    json_data = data.to_dict(orient='records')

    # Return JSON response
    return jsonify(json_data)





def recommend_top_mutual_funds_mid_cap(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '1Y' column to numeric after removing '%' symbol
    data['1Y'] = pd.to_numeric(data['1Y'].str.rstrip('%'), errors='coerce')


#   # Replace NaN values with a placeholder (e.g., -1)
#     data['1Y'].fillna(-1, inplace=True)
    data['1Y'].fillna(-1, inplace=True)


    # Sort the DataFrame based on '1Y' in descending order
    sorted_data = data.sort_values(by='1Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '1Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_mid_cap_mutual_funds_1Y', methods=['GET'])
def get_top_mutual_funds_mid_cap():
    # Get parameters from the request if needed
    # For example, you can use request.args.get('top_n', type=int, default=10) to get the 'top_n' parameter

    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_mid_cap()

    # Return the top mutual funds as a JSON response
    return jsonify({'top_mutual_funds': top_mutual_funds})


def recommend_top_mutual_funds_mid_cap_3Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '3Y' column to numeric after removing '%' symbol
    data['3Y'] = pd.to_numeric(data['3Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with NaN values in the '3Y' column
    data.dropna(subset=['3Y'], inplace=True)

    # Sort the DataFrame based on '3Y' in descending order
    sorted_data = data.sort_values(by='3Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '3Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict


@app.route('/get_mid_cap_mutual_funds_3Y', methods=['GET'])
def get_top_mutual_funds_mid_cap_3Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_mid_cap_3Y()

    # Return the top mutual funds as a JSON response with '3Y' key
    return jsonify({'top_mutual_funds_3Y': top_mutual_funds})





# MID CAP FUNDS 5 YEAR RETURNS
def recommend_top_mutual_funds_mid_cap_5Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '5Y' column to numeric after removing '%' symbol
    data['5Y'] = pd.to_numeric(data['5Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with NaN values in the '5Y' column
    data.dropna(subset=['5Y'], inplace=True)

    # Sort the DataFrame based on '5Y' in descending order
    sorted_data = data.sort_values(by='5Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '5Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_mid_cap_mutual_funds_5Y', methods=['GET'])
def get_top_mutual_funds_mid_cap_5Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_mid_cap_5Y()

    # Return the top mutual funds as a JSON response with '5Y' key
    return jsonify({'top_mutual_funds_5Y': top_mutual_funds})


# # MID CAP FUNDS 10 YEAR RETURNS
def recommend_top_mutual_funds_mid_cap_10Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '10Y' column to numeric after removing '%' symbol
    data['10Y'] = pd.to_numeric(data['10Y'].str.rstrip('%'), errors='coerce')

    # data['10Y'].fillna(-1, inplace=True)


    # Drop rows with NaN values in the '10Y' column
    data.dropna(subset=['10Y'], inplace=True)


    # Sort the DataFrame based on '10Y' in descending order
    sorted_data = data.sort_values(by='10Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '10Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_mid_cap_mutual_funds_10Y', methods=['GET'])
def get_top_mutual_funds_mid_cap_10Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_mid_cap_10Y()

    # Return the top mutual funds as a JSON response with '10Y' key
    return jsonify({'top_mutual_funds_10Y': top_mutual_funds})



##################################################################### Large Cap Mutual Funds ###########################################################################



@app.route('/large_cap_data')
def index_large_cap():
    # Sample data (replace this with your actual data)
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '1Y' column to numeric after removing '%' symbol
    data['1Y'] = pd.to_numeric(data['1Y'].str.rstrip('%'), errors='coerce')

    # Convert '1Y' column to numeric after removing '%' symbol
    data['3Y'] = pd.to_numeric(data['3Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with 'NaN' in the '1Y' column
    data = data.dropna(subset=['1Y'])

    # Drop rows with 'NaN' in the '1Y' column
    data = data.dropna(subset=['3Y'])

    # Drop duplicate entries based on 'Scheme Name'
    data = data.drop_duplicates(subset=['Scheme Name'], keep='first')

    # Convert the data to JSON
    json_data = data.to_dict(orient='records')

    # Return JSON response
    return jsonify(json_data)





def recommend_top_mutual_funds_large_cap(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '1Y' column to numeric after removing '%' symbol
    data['1Y'] = pd.to_numeric(data['1Y'].str.rstrip('%'), errors='coerce')


#   # Replace NaN values with a placeholder (e.g., -1)
#     data['1Y'].fillna(-1, inplace=True)
    data['1Y'].fillna(-1, inplace=True)


    # Sort the DataFrame based on '1Y' in descending order
    sorted_data = data.sort_values(by='1Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '1Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_large_cap_mutual_funds_1Y', methods=['GET'])
def get_top_mutual_funds_large_cap():
    # Get parameters from the request if needed
    # For example, you can use request.args.get('top_n', type=int, default=10) to get the 'top_n' parameter

    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_large_cap()

    # Return the top mutual funds as a JSON response
    return jsonify({'top_mutual_funds': top_mutual_funds})


def recommend_top_mutual_funds_large_cap_3Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '3Y' column to numeric after removing '%' symbol
    data['3Y'] = pd.to_numeric(data['3Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with NaN values in the '3Y' column
    data.dropna(subset=['3Y'], inplace=True)

    # Sort the DataFrame based on '3Y' in descending order
    sorted_data = data.sort_values(by='3Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '3Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict


@app.route('/get_large_cap_mutual_funds_3Y', methods=['GET'])
def get_top_mutual_funds_large_cap_3Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_large_cap_3Y()

    # Return the top mutual funds as a JSON response with '3Y' key
    return jsonify({'top_mutual_funds_3Y': top_mutual_funds})





# LARGE CAP FUNDS 5 YEAR RETURNS
def recommend_top_mutual_funds_large_cap_5Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '5Y' column to numeric after removing '%' symbol
    data['5Y'] = pd.to_numeric(data['5Y'].str.rstrip('%'), errors='coerce')

    # Drop rows with NaN values in the '5Y' column
    data.dropna(subset=['5Y'], inplace=True)

    # Sort the DataFrame based on '5Y' in descending order
    sorted_data = data.sort_values(by='5Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '5Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_large_cap_mutual_funds_5Y', methods=['GET'])
def get_top_mutual_funds_large_cap_5Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_large_cap_5Y()

    # Return the top mutual funds as a JSON response with '5Y' key
    return jsonify({'top_mutual_funds_5Y': top_mutual_funds})


# # LARGE CAP FUNDS 10 YEAR RETURNS
def recommend_top_mutual_funds_large_cap_10Y(top_n=65):
    # Replace the URL with the actual URL you want to fetch data from
    data = pd.read_html('https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html')[0]

    # Convert '10Y' column to numeric after removing '%' symbol
    data['10Y'] = pd.to_numeric(data['10Y'].str.rstrip('%'), errors='coerce')

    # data['10Y'].fillna(-1, inplace=True)


    # Drop rows with NaN values in the '10Y' column
    data.dropna(subset=['10Y'], inplace=True)


    # Sort the DataFrame based on '10Y' in descending order
    sorted_data = data.sort_values(by='10Y', ascending=False)

    # Add a new column 'Rank' to represent the ranking
    sorted_data['Rank'] = range(1, len(sorted_data) + 1)

    # Get the top N mutual funds
    top_funds = sorted_data.head(top_n)

    # Create a dictionary to represent the top mutual funds
    top_funds_dict = top_funds[['Rank', 'Scheme Name', '10Y', 'AuM (Cr)']].to_dict(orient='records')

    return top_funds_dict

@app.route('/get_large_cap_mutual_funds_10Y', methods=['GET'])
def get_top_mutual_funds_large_cap_10Y():
    # Call the recommendation function
    top_mutual_funds = recommend_top_mutual_funds_large_cap_10Y()

    # Return the top mutual funds as a JSON response with '10Y' key
    return jsonify({'top_mutual_funds_10Y': top_mutual_funds})
#####################################################################################








if __name__ == '__main__':
    app.run(debug=True)