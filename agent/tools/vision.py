import datetime
from PIL import ImageGrab

from agent.chains import VisionChain
from agent.path import IMAGE_DIR
from agent.db import store_image_desc, query_by_text
from agent.tool_registry import common_tool_registry
from agent.utils import load_locale_const

const = load_locale_const()

@common_tool_registry(
    name_or_callable="get_image_from_screen",
    description=const.GET_IMAGE_FROM_SCREEN_CONST['desc']
)
def get_image_from_screen(query: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = IMAGE_DIR / f"screenshot_{timestamp}.png"
    image = ImageGrab.grab()
    image.save(output_file_path)
    return output_file_path

@common_tool_registry(
    name_or_callable="get_image_from_db",
    description=const.GET_IMAGE_FROM_DB_CONST['desc']
)
def get_image_from_db(query: str) -> str:
    metadatas = query_by_text(query).get('metadatas', None)
    image_path = metadatas[0][0].get('image_path', None) if metadatas else None
    return image_path if image_path else ''

vision_chain = VisionChain()
@common_tool_registry(
    name_or_callable="vision_tool",
    description=const.VISION_TOOL_CONST['desc']
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