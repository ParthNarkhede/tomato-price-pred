from django.shortcuts import render
from .ml_model import PricePredictor
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

def price_prediction_view(request):
    if request.method == 'POST':
        user_date = request.POST.get('date')
        predictor = PricePredictor()

        # Get prediction results
        prediction_results = predictor.predict_price(user_date)

        if isinstance(prediction_results, str):
            # In case of an error, display it on the results page
            return render(request, 'prediction_result.html', {'error': prediction_results, 'date': user_date})

        # Extract prediction values
        modal_price = prediction_results['Predicted Modal Price']
        min_price = prediction_results['Predicted Min Price']
        max_price = prediction_results['Predicted Max Price']

        # Generate a yearly forecast graph
        fig, ax = plt.subplots(figsize=(8, 5))
        year = pd.to_datetime(user_date).year
        year_forecast = predictor.forecast[predictor.forecast['ds'].dt.year == year]
        ax.plot(year_forecast['ds'], year_forecast['yhat'], label='Yearly Forecast')
        ax.fill_between(year_forecast['ds'], year_forecast['yhat_lower'], year_forecast['yhat_upper'], color='gray', alpha=0.2)
        ax.set_title(f"Yearly Forecast for {year}")
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        year_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Generate a monthly forecast graph
        fig, ax = plt.subplots(figsize=(8, 5))
        month = pd.to_datetime(user_date).month
        month_forecast = predictor.forecast[(predictor.forecast['ds'].dt.year == year) & (predictor.forecast['ds'].dt.month == month)]
        ax.plot(month_forecast['ds'], month_forecast['yhat'], label='Monthly Forecast')
        ax.fill_between(month_forecast['ds'], month_forecast['yhat_lower'], month_forecast['yhat_upper'], color='gray', alpha=0.2)
        ax.set_title(f"Monthly Forecast for {year}-{month}")
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        month_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Generate the general forecast graph (for overall prediction)
        fig, ax = plt.subplots(figsize=(10, 6))
        future = predictor.future
        forecast = predictor.forecast
        ax.plot(future['ds'], forecast['yhat'], label='General Forecast')
        ax.fill_between(future['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2)
        ax.set_title('General Forecast')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price (Rs./Quintal)')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        general_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Pass the prediction values and graphs to the template
        return render(request, 'prediction_result.html', {
            'modal_price': modal_price,
            'min_price': min_price,
            'max_price': max_price,
            'year_graph': year_graph,
            'month_graph': month_graph,
            'general_graph': general_graph,
            'date': user_date
        })

    return render(request, 'prediction_form.html')
