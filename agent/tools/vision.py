import datetime
from PIL import ImageGrab

from agent.chains import VisionChain
from agent.path import IMAGE_DIR
from agent.db import store_image_desc, query_by_text
from agent.tool_registry import common_tool_registry

@common_tool_registry(
    name_or_callable="get_image_from_screen",
    description="""
    Takes a screenshot, saves it as a file, and returns the file path.
    
    Args:
        query (str): User's question or request (e.g., "Take a screenshot of what I'm seeing now and tell me the filename.", "Don't you want to see the video I'm watching? Take a screenshot of the current window.")
    
    Returns:
        str: The file path of the screenshot just taken
    """
)
def get_image_from_screen(query: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = IMAGE_DIR / f"screenshot_{timestamp}.png"
    image = ImageGrab.grab()
    image.save(output_file_path)
    return output_file_path

@common_tool_registry(
    name_or_callable="get_image_from_db",
    description="""
    When you want to see a photo used in a previous conversation again, use this tool to get the filename of the photo by using a description or message record at that time as a query.
    
    Args:
        query (str): Query to find the photo (e.g., "The photo you reacted to as 'a scene from a comic where Superman and Batman are fighting' before", "The photo of a dog running in front of the blue sea")
    
    Returns:
        str: The file path of the photo found by the query. If the photo is not found or an error occurs, returns an empty string.
    """
)
def get_image_from_db(query: str) -> str:
    metadatas = query_by_text(query).get('metadatas', None)
    image_path = metadatas[0][0].get('image_path', None) if metadatas else None
    return image_path if image_path else ''

vision_chain = VisionChain()
@common_tool_registry(
    name_or_callable="vision_tool",
    description="""
    Responds using both the user's query and the image at the same time.
    When the user includes the image file path directly in the question, or when an image is needed in the current context, this tool is called with the image path to obtain a multimodal answer.
    
    Args:
        query (str): User's question or request (e.g., "Describe this photo.", "What is the name of the character on the left side of this picture?")
        image_path (str): File path of the attached image
    Returns:
        str: Answer to the user's query (using the image)
    """
)
def vision_tool(query: str, image_path: str) -> str:
    from langchain_core.messages import HumanMessage, messages_from_dict
    from agent.utils import load_chat_memory

    def encode_image(path: str) -> tuple[str, str]:
        import base64, mimetypes
        mime = mimetypes.guess_type(path)[0]
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return mime, b64
    
    mime, b64 = encode_image(image_path)
    input = [
        HumanMessage(
            content=[
                {"type": "text", "text": query},
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": b64,
                    "mime_type": mime
                }
            ]
        )
    ]
    memory = []
    messages_dict = load_chat_memory()
    if messages_dict is not None: 
        memory = messages_from_dict(messages_dict) 

    response = vision_chain.invoke({"memory":memory, "input": input})
    store_image_desc(image_path, response)
    return response