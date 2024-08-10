from typing import Optional, Type

from langchain.tools.base import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel, Field


class PythonInput(BaseModel):
    code: str = Field(
        description="A valid Python script. The last operation must store the output value in a variable called `result`")


class PythonCodeInterpreter(BaseTool):
    name = "PythonCodeInterpreter"
    description = """
    Execute Python code. Useful to do computations and get fresh data (for example the current date and time).

    Examples:

    - {"code": \"\"\"import datetime\nresult = datetime.datetime.now()\n\"\"\"}
    - {"code": \"\"\"a = 5\nb = 3\nresult = a + b\n\"\"\"}
    - {"code": \"\"\"import math\nresult = math.sqrt(25)\n\"\"\"}
    """

    args_schema: Type[BaseModel] = PythonInput

    def _run(
        self,
        code: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:

        local_vars = {}
        exec(code, {}, local_vars)
        result_value = local_vars.get('result')

        if not result_value:
            raise ValueError(
                "The last operation of the code provided must store the output of the code in a variable called result.")

        return str(result_value)

    def get_tool_start_message(self, input: dict) -> str:
        payload = PythonInput(**input)
        return f"Executing code:\n\n <code>{payload.code}</code>"
