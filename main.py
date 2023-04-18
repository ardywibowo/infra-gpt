from fastapi import FastAPI, APIRouter, Response, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import uvicorn

router = APIRouter()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def output_check(output_string):
    # If the output string has more than 2000 characters, get the last 2000 characters
    if len(output_string) > 10000:
        print("removing some text")
        # Get the last 4000 characters
        output_string = output_string[-10000:]
        # Find the position of the first newline character in the truncated string
        newline_pos = output_string.find('\n')
        # If a newline character is found, start the output from the character after the newline
        if newline_pos != -1:
            output_string = output_string[newline_pos + 1:]
    return output_string


@router.get("/get_available_commands/")
async def get_available_commands():
    print("print getting available commands")
    output_string = subprocess.check_output('dpkg-query -l | grep "^ii" | awk \'$3 != "ubuntu-minimal" {print $2}\'', shell=True)
    # output_string = subprocess.check_output(command, shell=True)
    print(output_string)
    return Response(content=output_string, media_type="text/plain", status_code=200)


@app.get("/run_cmd/{command:path}")
async def run_cmd(command: str):
    print("attempting to run", command)
    try:
        output_string = subprocess.check_output(command, shell=True).decode()
        print(output_string)
        # Apply the output check
        output_string = output_check(output_string)
        return Response(content=output_string, media_type="text/plain", status_code=200)
    except Exception as e:
        try:
            sudo_command = f"sudo {command}"
            output_string = subprocess.check_output(sudo_command, shell=True, timeout=15).decode()
            print(output_string)
            # Apply the output check
            output_string = output_check(output_string)
            return Response(content=output_string, media_type="text/plain", status_code=200)
        except Exception as e:
            return Response(content=str(e), media_type="text/plain", status_code=500)

@app.get("/install_cmd/{ins_package:path}")
async def install_cmd(ins_package: str):
    """
    install a ubuntu package using sudo
    """
    print("installing", ins_package)
    try:
        # Run the command and capture both stdout and stderr
        result = subprocess.run(["sudo", "apt-get", "install", "-y", ins_package],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Check the return code to determine success or failure
        if result.returncode == 0:
            output_string = result.stdout
            # Apply the output check
            output_string = output_check(output_string)
            return Response(content=output_string, media_type="text/plain", status_code=200)
        else:
            output_string = result.stderr
            # Apply the output check
            output_string = output_check(output_string)
            return Response(content=output_string, media_type="text/plain", status_code=400)  # Bad Request
    except Exception as e:
        # Handle other exceptions and set the output_string to the error message
        output_string = str(e)
        return Response(content=output_string, media_type="text/plain", status_code=500)  # Internal Server Error
    

@router.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@router.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(text, media_type="text/json")

@router.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, media_type="text/yaml")
    
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5003, log_level="info")