@echo off
echo Setting up MCP Server...

REM Create a virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    uv venv
)

REM Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
uv pip install -r requirements.txt

echo.
echo Setup complete! You can now run the server with:
echo python run.py
pause

@REM Made with Bob
