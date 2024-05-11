from cairosvg import svg2png

def svg_to_png_bytes(svg_string):
  png_bytes = svg2png(bytestring=svg_string.encode('utf-8'))
  return png_bytes

def python_math_execution(math_string):
  try:
    answer = eval(math_string)
    if answer:
      return str(answer)
  except:
    return 'invalid code generated'

def generate_image(prompt: str):
    if "generate an image" in prompt.lower():
        return "Sure, I'll get right on that!"
    else:
        return "No suitable image type found for the prompt."
    
def run_function(name: str, args: dict):
  if name == "svg_to_png_bytes":
      return svg_to_png_bytes(args["svg_string"])
  elif name == "python_math_execution":
      return python_math_execution(args["math_string"])
  elif name == "generate_image":
      return generate_image(args["prompt"])
  else:
      return None

functions = [
    {
        "type": "function",
        "function": {
            "name": "svg_to_png_bytes",
            "description": "Generate a PNG from an SVG",
            "parameters": {
                "type": "object",
                "properties": {
                    "svg_string": {
                        "type":
                        "string",
                        "description":
                        "A fully formed SVG element in the form of a string",
                    },
                },
                "required": ["svg_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "python_math_execution",
            "description": "Solve a math problem using python code",
            "parameters": {
                "type": "object",
                "properties": {
                    "math_string": {
                        "type":
                        "string",
                        "description":
                        "A string that solves a math problem that conforms with python syntax that could be passed directly to an eval() function",
                    },
                },
                "required": ["math_string"],
            },
        },
    },
    {
       "type": "function",
        "function": {
        "name": "generate_image",
        "description": "Generates an image based on a user's prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A user's prompt suggesting the type of image to generate",
                },
            },
            "required": ["prompt"],
        },
      }
    }
]

