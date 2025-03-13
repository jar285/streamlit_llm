"""System prompts for different assistant types."""
from typing import Dict, List, Any, Optional

class AssistantType:
    """Defines a type of AI assistant with specialized system prompt."""
    
    def __init__(self, 
                id: str,
                name: str, 
                system_prompt: str,
                description: Optional[str] = None,
                icon: Optional[str] = None):
        """Initialize an assistant type.
        
        Args:
            id: Unique identifier for this assistant type
            name: Display name for this assistant type
            system_prompt: System prompt text to use
            description: Optional description of this assistant type
            icon: Optional emoji icon for this assistant type
        """
        self.id = id
        self.name = name
        self.system_prompt = system_prompt
        self.description = description or ""
        self.icon = icon or "🤖"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "system_prompt": self.system_prompt,
            "description": self.description,
            "icon": self.icon
        }


class SystemPromptManager:
    """Manages system prompts for different assistant types."""
    
    def __init__(self):
        """Initialize with default assistant types."""
        self.assistant_types = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize default assistant types."""
        # General assistant (default)
        self.add_assistant_type(AssistantType(
            id="general",
            name="General Assistant",
            system_prompt="You are a helpful, harmless, and honest AI assistant. Always answer as helpfully as possible.",
            description="A well-rounded assistant for general tasks and questions",
            icon="💬"
        ))
        
        # Coding expert
        self.add_assistant_type(AssistantType(
            id="coding",
            name="Coding Expert",
            system_prompt="""You are a coding expert AI assistant. Focus on providing clear, efficient, and well-documented code solutions.
Follow these principles:
1. First understand the requirements thoroughly.
2. Provide working code with explanations.
3. Highlight best practices and potential improvements.
4. If you spot issues in the user's approach, suggest better alternatives.
5. For complex solutions, break down the implementation steps.
6. Include comments in code to explain key parts.
7. If relevant, mention performance considerations.""",
            description="Specialized in programming assistance, code review, and software development",
            icon="👩‍💻"
        ))
        
        # Financial advisor
        self.add_assistant_type(AssistantType(
            id="finance",
            name="Financial Advisor",
            system_prompt="""You are a financial advisor AI assistant. Provide helpful information on financial topics while following these guidelines:
1. Clarify that your advice is informational, not professional financial advice.
2. Explain financial concepts clearly without unnecessary jargon.
3. When discussing investments, emphasize the importance of diversification and risk management.
4. Avoid making specific investment recommendations about individual securities.
5. Encourage users to consult with qualified financial professionals for their specific situation.
6. Provide educational content on financial planning, budgeting, investing concepts, and economic topics.""",
            description="Specialized in financial advice, investment concepts, and economic information",
            icon="💰"
        ))
    
    def add_assistant_type(self, assistant_type: AssistantType) -> None:
        """Add an assistant type to the manager.
        
        Args:
            assistant_type: The assistant type to add
        """
        self.assistant_types[assistant_type.id] = assistant_type
    
    def get_assistant_type(self, type_id: str) -> Optional[AssistantType]:
        """Get an assistant type by ID.
        
        Args:
            type_id: ID of the assistant type to get
            
        Returns:
            The assistant type or None if not found
        """
        return self.assistant_types.get(type_id)
    
    def get_default_assistant_type(self) -> AssistantType:
        """Get the default assistant type.
        
        Returns:
            The default assistant type
        """
        return self.assistant_types["general"]
    
    def get_all_assistant_types(self) -> List[AssistantType]:
        """Get all available assistant types.
        
        Returns:
            List of all assistant types
        """
        return list(self.assistant_types.values())
    
    def get_system_prompt(self, type_id: str) -> str:
        """Get the system prompt for a given assistant type.
        
        Args:
            type_id: ID of the assistant type
            
        Returns:
            The system prompt text or default if type not found
        """
        assistant_type = self.get_assistant_type(type_id)
        if assistant_type:
            return assistant_type.system_prompt
        return self.get_default_assistant_type().system_prompt


# Create a singleton instance
system_prompt_manager = SystemPromptManager()