import pandas as pd
import colorsys
from typing import Union, Optional
import pandas as pd
from datetime import datetime

class PostcardDataToolkit:
    '''A collection of utility methods for processing and filtering
    Postcrossing Data for time-series analysis.
    '''

    @staticmethod
    def filter_by_date(df: pd.DataFrame, 
                       date_col: str = 'sent_date', 
                       start_date: Union[str, datetime, pd.Timestamp] = '2015-01-01', 
                       end_date: Optional[Union[str, datetime, pd.Timestamp]] = None
                       ) -> pd.DataFrame:
        '''Filter the DataFrame for postcards sent within a specific date range.
        Parameters: df (pd.DataFrame): The input DataFrame containing the (prefiltered) data.
                    date_col (str): The name of the date column to filter by. Default is 'sent_date'.
                    start_date (str, datetime or pd.Timestamp): The start date for filtering (inclusive). Default is January 1, 2015. format is yyyy-mm-dd. 
                    end_date (str, datetime, pd.Timestamp or None): The end date for filtering (inclusive). If None, no upper limit is applied.
        '''
        df_filtered = df.copy()
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date) if end_date else None
        
        mask = df_filtered[date_col] >= start
        if end:
            if end < start:
                raise ValueError("End date cannot be earlier than start date.")
            mask &= df_filtered[date_col] <= end

        return df_filtered.loc[mask].copy()

    @staticmethod
    def filter_origin_countries(df: pd.DataFrame,
                                country_codes: list[str] | str
                                ) -> pd.DataFrame:
        '''Filter the DataFrame for specific origin country codes.
        Parameters: df (pd.DataFrame): The input DataFrame containing the (prefiltered) data.
                    country_codes (list of str or str): A list of ISO 3166-1 alpha-2 codes (e.g., ['DE', 'GB']) or a single code.
        Returns: pd.DataFrame: A new containing only the selected origin countries.
        '''
        if isinstance(country_codes, str):
            country_codes = [country_codes]

        df_filtered = df[df['country_id_origin'].isin(country_codes)].copy()
        
        return df_filtered
    
    @staticmethod
    def filter_destination_countries(df: pd.DataFrame, 
                                     country_codes: list[str] | str
                                     ) -> pd.DataFrame:
        '''Filter the DataFrame for specific destination country codes.
        Parameters: df (pd.DataFrame): The input DataFrame containing the (prefiltered) data.
                    country_codes (list of str or str): A list of ISO 3166-1 alpha-2 codes (e.g., ['DE', 'GB']) or a single code.
        Returns: pd.DataFrame: A new containing only the selected destination countries.
        '''
        if isinstance(country_codes, str):
            country_codes = [country_codes]

        df_filtered = df[df['country_id_dest'].isin(country_codes)].copy()
        
        return df_filtered
    
    @staticmethod
    def filter_user_countries(df: pd.DataFrame, 
                              country_codes: list[str] | str
                              ) -> pd.DataFrame:
        '''Filter the DataFrame for specific user country codes.
        Parameters: df (pd.DataFrame): The input DataFrame containing the (prefiltered) data.
                    country_codes (list of str or str): A list of ISO 3166-1 alpha-2 codes (e.g., ['DE', 'GB']) or a single code.
        Returns: pd.DataFrame: A new containing only the selected user countries.
        '''
        if isinstance(country_codes, str):
            country_codes = [country_codes]

        df_filtered = df[df['user_country'].isin(country_codes)].copy()
        
        return df_filtered
    
class PlottingToolkit:

    @staticmethod
    def adjust_color_lightness(hex_color: str, amount: float = 0.5) -> str:
        """
        amount < 1.0 for darker color, amount > 1.0 for brighter color.
        """
        hex_color = hex_color.lstrip('#')
        rgb = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
        # Conversion to HLS (Hue, Lightness, Saturation)
        h, l, s = colorsys.rgb_to_hls(*rgb)
        # Adjust brightness
        l = max(0, min(1, l * amount))
        # -> RGB -> Hex
        rgb = colorsys.hls_to_rgb(h, l, s)
        return '#%02x%02x%02x' % tuple(int(x*255) for x in rgb)
    
class CountryToolkit:

    COUNTRY_MAPPING = {
            "NL": "Netherlands", "FR": "France", "GB": "UK",
            "DE": "Germany", "PL": "Poland", "CZ": "Czechia", "HU": "Hungary",
            "FI": "Finland", "NO": "Norway",
            "BY": "Belarus", "RU": "Russia",
            "CA": "Canada", "BR": "Brazil", "US": "U.S.A.",
            "CN": "China", "TW": "Taiwan", "AU": "Australia"
        }

    @staticmethod
    def get_country_name(country_code: str) -> str:
        """Changes ISO-Code into full name, uses pycountry as fallback.
        """
        if country_code in CountryToolkit.COUNTRY_MAPPING:
            return CountryToolkit.COUNTRY_MAPPING[country_code]
        
        try:
            import pycountry
            country = pycountry.countries.get(alpha_2=country_code)
            if country:
                return country.name
            
        except (ImportError, LookupError):
            pass
            
        return country_code
        