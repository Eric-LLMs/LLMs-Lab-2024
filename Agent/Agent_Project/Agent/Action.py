from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Action(BaseModel):
    name: str = Field(description="Tool or instruction name")
    args: Optional[Dict[str, Any]] = Field(description="Tool or instruction parameters, consisting of parameter names and values")
