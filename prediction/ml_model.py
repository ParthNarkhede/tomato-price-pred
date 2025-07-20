import os
import pandas as pd
from prophet import Prophet
from django.conf import settings

class PricePredictor:
    def __init__(self):
        # Path to the Excel file
        file_path = os.path.join(settings.BASE_DIR, 'prediction', 'data', 'Prices_Tomato_Cleaned.xlsx')

        # Load data and train the Prophet model
        self.data = pd.read_excel(file_path, parse_dates=['Reported Date'], engine='openpyxl')
        self.data = self.data[['Reported Date', 'Modal Price (Rs./Quintal)']].rename(
            columns={'Reported Date': 'ds', 'Modal Price (Rs./Quintal)': 'y'})
        self.model = Prophet()
        self.model.fit(self.data)

        # Generate future predictions
        self.future = self.model.make_future_dataframe(periods=365 * 3)
        self.forecast = self.model.predict(self.future)

    def predict_price(self, date_str):
        user_date = pd.to_datetime(date_str)

        # Check if the date is in the past or future
        if user_date < pd.to_datetime('2023-10-15'):  # Date is in the past
            historical_data = self.data[self.data['ds'] == user_date]
            if historical_data.empty:
                return f"No data available for {date_str}"
            modal_price = historical_data['y'].values[0]
            return {
                'Predicted Modal Price': modal_price,
                'Predicted Min Price': modal_price,  # Assuming min and max to be modal in the past
                'Predicted Max Price': modal_price
            }
        else:  # Future prediction using Prophet
            specific_forecast = self.forecast[self.forecast['ds'] == user_date]
            if specific_forecast.empty:
                return f"No prediction available for {date_str}"

            predicted_modal_price = specific_forecast['yhat'].values[0]
            predicted_min_price = specific_forecast['yhat_lower'].values[0]
            predicted_max_price = specific_forecast['yhat_upper'].values[0]

            return {
                'Predicted Modal Price': predicted_modal_price,
                'Predicted Min Price': predicted_min_price,
                'Predicted Max Price': predicted_max_price
            }
