import plotly.graph_objects as go
import pandas as pd
import argparse
import os

def plot_area_line_chart_with_labels(data, output_dir=".", output_file="usage_cost_trend_with_labels_and_grand_total.html"):
    df = pd.DataFrame(data)

    # Ensure usage columns and grand_total_baht are numerical
    df['usage_1_150_units'] = pd.to_numeric(df['usage_1_150_units'], errors='coerce')
    df['usage_151_400_units'] = pd.to_numeric(df['usage_151_400_units'], errors='coerce')
    df['usage_over_401_units'] = pd.to_numeric(df['usage_over_401_units'], errors='coerce')
    df['total_usage_units'] = pd.to_numeric(df['total_usage_units'], errors='coerce')
    df['grand_total_baht'] = pd.to_numeric(df['grand_total_baht'].str.replace(',', ''), errors='coerce')
    df['ft_adjustment_baht'] = pd.to_numeric(df['ft_adjustment_baht'], errors='coerce')
    df['ft_cost_per_unit'] = df['ft_adjustment_baht'] / df['total_usage_units']

    # Sort the dataframe by billing_period
    df = df.sort_values(by='billing_period')

    fig = go.Figure()

    # Stacked Area Chart for usage breakdown
    fig.add_trace(go.Scatter(
        x=df['billing_period'], 
        y=df['usage_1_150_units'], 
        name='Usage 1-150 Units',
        stackgroup='one',
        mode='none',  # No lines, just fill
        fillcolor='rgba(31, 119, 180, 0.6)'  # Blue with transparency
    ))
    fig.add_trace(go.Scatter(
        x=df['billing_period'], 
        y=df['usage_151_400_units'], 
        name='Usage 151-400 Units',
        stackgroup='one',
        mode='none', 
        fillcolor='rgba(255, 127, 14, 0.6)'  # Orange with transparency
    ))
    fig.add_trace(go.Scatter(
        x=df['billing_period'], 
        y=df['usage_over_401_units'], 
        name='Usage Over 401 Units',
        stackgroup='one',
        mode='none',
        fillcolor='rgba(44, 160, 44, 0.6)'  # Green with transparency
    ))

    # Line chart for grand total on the secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['billing_period'],
        y=df['grand_total_baht'],
        name='Grand Total (Baht)',
        mode='lines+markers',
        line=dict(color='firebrick', width=2),
        marker=dict(size=6)
    ))

    # Annotations for FT cost per unit, total usage, and grand total
    annotations = []
    for i, row in df.iterrows():
        # FT cost per unit annotation
        annotations.append(dict(
            x=row['billing_period'],
            y=-50,  # Adjust to be below the x-axis
            text=f"FT: {row['ft_cost_per_unit']:.4f} Baht/unit",
            showarrow=False,
            xanchor='center',
            yanchor='top',
            font=dict(size=10)
        ))

        # Total usage unit annotation
        annotations.append(dict(
            x=row['billing_period'],
            y=row['total_usage_units'] + 50,  # Show above the bar
            text=f"{row['total_usage_units']:.0f} Units",
            showarrow=False,
            xanchor='center',
            yanchor='bottom',
            font=dict(size=10, color="black")
        ))

        # Grand total annotation
        annotations.append(dict(
            x=row['billing_period'],
            y=row['grand_total_baht'] + 50,  # Show above the marker
            text=f"{row['grand_total_baht']:.2f} Baht",
            showarrow=False,
            xanchor='center',
            yanchor='bottom',
            font=dict(size=10, color="red")
        ))

    # Layout with two y-axes
    fig.update_layout(
        title='Usage Breakdown, Grand Total, and FT Cost per Unit',
        xaxis=dict(title='Billing Period'),
        yaxis=dict(title='Usage (Units)', rangemode='tozero'),
        yaxis2=dict(title='Grand Total (Baht)', overlaying='y', side='right', rangemode='tozero'),
        annotations=annotations,
        height=600,
        margin=dict(t=100, r=100, b=150, l=100),
        legend=dict(x=1.1, y=0.9),  # Legend on the right
        template='plotly_white'
    )

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save as an interactive HTML file
    output_path = os.path.join(output_dir, output_file)
    fig.write_html(output_path)

    print(f"Plot saved to {output_path}")

def main():
    # Argument parser for CLI usage
    parser = argparse.ArgumentParser(description="Generate usage and cost breakdown plot from CSV data")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_dir", help="Directory to save the generated HTML file")
    args = parser.parse_args()

    # Load CSV and convert to the format required by the function
    df = pd.read_csv(args.input_file)
    data = df.to_dict(orient='records')

    # Call the plot function
    plot_area_line_chart_with_labels(data, output_dir=args.output_dir)

if __name__ == "__main__":
    main()
