"""Appointment management functionality for Voice Assistant."""
import logging
from langchain_core.prompts import PromptTemplate

from ..prompts import PromptTemplates
from ..exceptions import ActionHandlerError

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
        self.prompts = PromptTemplates()
        logger.debug("🔍 AppointmentActions initialized with LLM")
    
    def cancel_appointment(self, text: str) -> str:
        """Simulate appointment cancellation and extract details.
        
        Args:
            text (str): User's cancellation request
            
        Returns:
            str: Response confirming cancellation
        """
        logger.info("🗑️ Processing appointment cancellation request")
        
        try:
            # Extract details from the request
            extraction_prompt = PromptTemplate(
                input_variables=["input"],
                template=self.prompts.appointment_extraction
            )
            
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
            raise ActionHandlerError("Failed to process appointment cancellation") from e
    
    def schedule_appointment(self, text: str) -> str:
        """Schedule a new appointment with required date and time.
        
        Args:
            text (str): User's scheduling request
            
        Returns:
            str: Response confirming scheduling or requesting more information
        """
        logger.info("📅 Processing appointment scheduling request")
        logger.debug(f"🔍 Appointment request text: \"{text}\"")
        
        try:
            # Extract details from the request
            extraction_prompt = PromptTemplate(
                input_variables=["input"],
                template=self.prompts.scheduling_extraction
            )
            
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
            
            # If title is missing or unclear, set a default
            if not title or title == "unspecified" or title == "[appointment title]" or "suggest" in title.lower():
                # Use LLM to infer an appropriate title
                infer_title_prompt = PromptTemplate(
                    input_variables=["input"],
                    template=self.prompts.title_inference
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
            logger.info(f"✅ Successfully scheduled: {title} on {date} at {time}")
            
            return f"I've scheduled your {title} for {date} at {time}. You will receive a confirmation email shortly."
                
        except Exception as e:
            logger.error(f"❌ Error extracting appointment details: {e}")
            raise ActionHandlerError("Failed to process appointment scheduling") from e 