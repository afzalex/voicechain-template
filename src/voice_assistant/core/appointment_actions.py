"""Appointment management functionality for Voice Assistant."""
import logging
from langchain.prompts import PromptTemplate

# Get logger
logger = logging.getLogger("voice-assistant")

class AppointmentActions:
    """Handles appointment scheduling and cancellation."""
    
    def __init__(self, llm):
        """Initialize with language model for processing.
        
        Args:
            llm: Language model for inference
        """
        self.llm = llm
        logger.debug("🔍 AppointmentActions initialized with LLM")
    
    def cancel_appointment(self, text):
        """Simulate appointment cancellation and extract details.
        
        Args:
            text (str): User's cancellation request
            
        Returns:
            str: Response confirming cancellation
        """
        logger.info("🗑️ DUMMY FUNCTION: Would have cancelled appointment here")
        
        # Use the LLM to extract appointment details from the text
        extraction_prompt = PromptTemplate(
            input_variables=["input"],
            template="""
            Extract appointment details from this request: {input}
            
            Return the details in this format:
            TITLE: [appointment title, or "unspecified" if not mentioned]
            DATE: [appointment date, or "unspecified" if not mentioned]
            TIME: [appointment time, or "unspecified" if not mentioned]
            
            If multiple appointments are mentioned, focus on the one most likely being cancelled.
            """
        )
        
        try:
            # Extract details from the request
            details_response = self.llm.invoke(extraction_prompt.format(input=text))
            logger.info(f"Extracted appointment details: {details_response}")
            
            # Parse the details
            title = "unspecified"
            date = "unspecified"
            time = "unspecified"
            
            for line in details_response.strip().split("\n"):
                if line.startswith("TITLE:"):
                    title = line[6:].strip()
                elif line.startswith("DATE:"):
                    date = line[5:].strip()
                elif line.startswith("TIME:"):
                    time = line[5:].strip()
            
            # In a real implementation, this would connect to a calendar service
            # and cancel the specific appointment that was found
            
            # Prepare a response that includes the details
            if date != "unspecified" and title != "unspecified":
                return f"I've cancelled your {title} appointment on {date}" + \
                       (f" at {time}" if time != "unspecified" else "") + \
                       ". You will receive a confirmation email shortly."
            elif date != "unspecified":
                return f"I've cancelled your appointment on {date}" + \
                       (f" at {time}" if time != "unspecified" else "") + \
                       ". You will receive a confirmation email shortly."
            elif title != "unspecified":
                return f"I've cancelled your {title} appointment. You will receive a confirmation email shortly."
            else:
                return "I've cancelled your appointment. You will receive a confirmation email shortly."
                
        except Exception as e:
            logger.error(f"Error extracting appointment details: {e}")
            return "I've cancelled your appointment. You will receive a confirmation email shortly."
    
    def schedule_appointment(self, text, normalize_date_func):
        """Schedule a new appointment with required date and time.
        
        Args:
            text (str): User's scheduling request
            normalize_date_func: Function to normalize date references
            
        Returns:
            str: Response confirming scheduling or requesting more information
        """
        logger.info("📅 Processing appointment scheduling request")
        logger.debug(f"🔍 Appointment request text: \"{text}\"")
        
        # Use the LLM to extract appointment details
        extraction_prompt = PromptTemplate(
            input_variables=["input"],
            template="""
            Extract appointment scheduling details from this request: {input}
            
            For DATES, recognize both relative dates ("tomorrow", "next Tuesday", "in 3 days") and specific dates 
            (like "October 2nd", "2nd of October", "Oct 2", "2 October", "10/02", etc.)
            
            For TIMES, recognize all formats (like "3 PM", "3:00", "3 o'clock", "15:00", "three in the afternoon", etc.)
            
            Return the details in this exact format - you MUST include all three lines:
            TITLE: [appointment title, or suggest an appropriate title if none is explicitly mentioned]
            DATE: [the date mentioned in the request, exactly as spoken]
            TIME: [the time mentioned in the request, exactly as spoken]
            
            If no date or time is mentioned at all, write "unspecified" for that field.
            Consider variations in how people express dates and times.
            """
        )
        
        try:
            # Extract details from the request
            logger.debug("🔍 Extracting appointment details from text using LLM")
            details_response = self.llm.invoke(extraction_prompt.format(input=text))
            logger.info(f"📋 Extracted appointment details: {details_response}")
            
            # Parse the details
            title = None
            date = None
            time = None
            
            for line in details_response.strip().split("\n"):
                if line.startswith("TITLE:"):
                    title = line[6:].strip()
                elif line.startswith("DATE:"):
                    date = line[5:].strip()
                elif line.startswith("TIME:"):
                    time = line[5:].strip()
            
            logger.debug(f"🔍 Parsed fields - Title: '{title}', Date: '{date}', Time: '{time}'")
            
            # Check if date and time are valid
            invalid_terms = ["unspecified", "not specified", "no specific", "none", "not mentioned"]
            
            # Check if required fields are provided and valid
            missing_fields = []
            if not date or any(term in date.lower() for term in invalid_terms):
                missing_fields.append("date")
                logger.debug(f"🔍 Missing required field: date")
            if not time or any(term in time.lower() for term in invalid_terms):
                missing_fields.append("time")
                logger.debug(f"🔍 Missing required field: time")
            
            # Handle missing required fields
            if missing_fields:
                fields_str = ", ".join(missing_fields)
                logger.info(f"⚠️ Cannot schedule: missing {fields_str}")
                return f"I need {fields_str} to schedule your appointment. Please provide this information."
            
            # Normalize relative date references to actual dates
            normalized_date = normalize_date_func(date)
            logger.debug(f"🔍 Normalized date: '{date}' → '{normalized_date}'")
            
            # If title is missing or unclear, set a default
            if not title or title == "unspecified" or title == "[appointment title]" or "suggest" in title.lower():
                # Use LLM to infer an appropriate title
                infer_title_prompt = PromptTemplate(
                    input_variables=["input"],
                    template="""
                    Based on this appointment scheduling request: {input}
                    
                    Infer a single appropriate, brief title for this appointment (3 words maximum).
                    Return only the title without any explanation or additional text.
                    """
                )
                
                try:
                    logger.debug("🔍 Inferring appointment title")
                    inferred_title = self.llm.invoke(infer_title_prompt.format(input=text)).strip()
                    title = inferred_title if inferred_title else "General Appointment"
                    logger.info(f"📝 Inferred appointment title: {title}")
                except Exception as e:
                    logger.error(f"❌ Error inferring title: {e}")
                    title = "General Appointment"
            
            # In a real implementation, this would connect to a calendar service
            # and schedule the appointment with the extracted details
            logger.info(f"✅ Successfully scheduled: {title} on {normalized_date} at {time}")
            
            return f"I've scheduled your {title} for {normalized_date} at {time}. You will receive a confirmation email shortly."
                
        except Exception as e:
            logger.error(f"❌ Error extracting appointment details: {e}")
            return "I couldn't schedule your appointment. Please make sure to include at least a date and time." 