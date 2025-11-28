import pandas as pd
import streamlit as st

def convert_response_to_df(data: dict) -> pd.DataFrame:
    """Convert Weaviate response to pandas DataFrame with enhanced error handling"""
    try:
        df = pd.DataFrame(data=data)
        if '_additional' in df.columns:
            additional_df = pd.json_normalize(df['_additional'])
            df = df.drop(columns=['_additional'])
            df = pd.concat([additional_df, df], axis=1)
        return df
    except Exception as e:
        st.error(f"Error converting response to DataFrame: {str(e)}")
        return pd.DataFrame()

def format_data_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Format DataFrame for better display in Streamlit"""
    display_df = df.copy()
    
    # Format numeric columns
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'float32']:
            if col == 'score':
                display_df[col] = display_df[col].round(4)
            else:
                display_df[col] = display_df[col].round(2)
    
    return display_df

def get_data_insights(df: pd.DataFrame) -> dict:
    """Generate insights about the data"""
    if df.empty:
        return {}
    
    insights = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'text_columns': len(df.select_dtypes(include=['object']).columns),
        'missing_values': df.isnull().sum().sum(),
    }
    
    if 'score' in df.columns:
        insights['avg_score'] = df['score'].mean()
        insights['max_score'] = df['score'].max()
        insights['min_score'] = df['score'].min()
    
    return insights
