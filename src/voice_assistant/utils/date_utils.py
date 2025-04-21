"""Date utilities for Voice Assistant."""
import re
import datetime

def normalize_date(date_text):
    """Convert relative date references to actual dates.
    
    Args:
        date_text (str): A date reference like "tomorrow", "next Tuesday", etc.
        
    Returns:
        str: A formatted date string like "Monday, January 1, 2024"
    """
    today = datetime.datetime.now().date()
    
    # Handle common relative date patterns
    date_text = date_text.lower()
    
    # Handle "tomorrow"
    if "tomorrow" in date_text:
        result_date = today + datetime.timedelta(days=1)
        return result_date.strftime("%A, %B %d, %Y")
    
    # Handle "today"
    if "today" in date_text:
        return today.strftime("%A, %B %d, %Y")
    
    # Handle "X days later/from now/from today"
    days_pattern = re.search(r'(\d+)\s*days?\s*(later|from now|from today)', date_text)
    if days_pattern:
        days = int(days_pattern.group(1))
        result_date = today + datetime.timedelta(days=days)
        return result_date.strftime("%A, %B %d, %Y")
    
    # Handle "next week"
    if "next week" in date_text:
        result_date = today + datetime.timedelta(days=7)
        return result_date.strftime("%A, %B %d, %Y")
    
    # Handle day of week references
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days_of_week):
        if day in date_text:
            # Calculate days until the next occurrence of this day
            today_weekday = today.weekday()  # 0 = Monday, 6 = Sunday
            days_until = (i - today_weekday) % 7
            
            # If "next" is specified, add 7 days
            if "next" in date_text:
                days_until += 7
            
            # If it's the same day and no "next" specified, and it's a simple day reference,
            # assume the user means next week's occurrence
            if days_until == 0 and "next" not in date_text and len(date_text.split()) <= 2:
                days_until = 7
            
            result_date = today + datetime.timedelta(days=days_until)
            return result_date.strftime("%A, %B %d, %Y")
    
    # If we couldn't parse it as a relative date, return the original text
    # This handles cases like "December 25th" or other specific date formats
    return date_text 