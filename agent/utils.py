from __future__ import annotations

import inspect
import json
import os
import tarfile
import textwrap
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Literal, Tuple

import requests
import yaml
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.model import ChainConfig
from agent.path import DESC_DIR, MEMORY_DIR

# --------------------------------------------------------------------------- #
# Prompt related
# --------------------------------------------------------------------------- #
def load_prompt(
    chain_config: ChainConfig, **vars_: Any
) -> Tuple[List[SystemMessage], List[AIMessage | HumanMessage]]:
    """
    Render a YAML prompt template and split it into *system* and *few-shot* messages.

    The YAML file may contain `${PLACEHOLDER}` variables. They will be substituted
    with the values provided via ``**vars_`` before the YAML is parsed.

    Args
    ----------
    chain_config : ChainConfig
        Configuration object whose ``yaml`` attribute points to the prompt file.
    **vars_ : Any
        Placeholder values to be injected into the template.  Multiline values are
        indented automatically so the resulting YAML stays valid.

    Returns
    -------
    tuple[list, list]
        ``system`` (length == 1) and ``few_shot`` message lists that can be fed
        directly into :class:`langchain.prompts.ChatPromptTemplate`.
    """
    with open(chain_config.yaml, "r", encoding="utf-8") as fh:
        raw = fh.read()

    # If a value contains newlines, indent it so YAML keeps the block structure.
    safe_vars = {
        k: v if "\n" not in str(v) else textwrap.indent(str(v), "  ")
        for k, v in vars_.items()
    }
    rendered = Template(raw).safe_substitute(**safe_vars)
    cfg = yaml.safe_load(rendered)
    
    system_messages = [SystemMessage(content=cfg.get('system', ''))]
    few_shot_messages = [
        HumanMessage(content=m["content"])
        if m["role"] == "human"
        else AIMessage(content=m["content"])
        for m in cfg.get('few_shot', [])
    ]
    return system_messages, few_shot_messages

def build_prompt(chain_config, extra_vars: dict = {}, extra_placeholders: list = []):
    """
    Constructs a ChatPromptTemplate by combining static prompt components with dynamic placeholders.

    This function performs the following steps:
      1. Loads the system messages and few-shot examples from the prompt file specified in the 
         chain configuration (chain_config). The extra_vars dictionary is used to customize these 
         components (for example, by injecting tool descriptions).
      2. Appends additional dynamic placeholders (using MessagesPlaceholder) defined by extra_placeholders. 
         These placeholders are intended for runtime insertion of values such as conversation memory or user input.
      3. Aggregates all the messages to create and return a ChatPromptTemplate that is ready for use in chain execution.

    Args:
        chain_config: An instance of ChainConfig, containing information (such as the file path) needed to load the prompt.
        extra_vars (dict): A dictionary of additional variables for customizing the prompt components.
        extra_placeholders (list): A list of variable names for which dynamic message placeholders should be created.

    Returns:
        ChatPromptTemplate: A prompt template object constructed from the loaded system messages, few-shot examples, 
                            and the specified message placeholders.
    """
    system_message, few_shot = load_prompt(chain_config, **extra_vars)
    messages = [
        *system_message,
        *few_shot,
        *[MessagesPlaceholder(variable_name=ph) for ph in extra_placeholders]
    ]
    return ChatPromptTemplate.from_messages(messages)


# --------------------------------------------------------------------------- #
# Tool description related
# --------------------------------------------------------------------------- #
def tool_desc_format(desc: Dict[str, Any]) -> str:
    """
    Convert a single tool-metadata dict to the markdown snippet used in prompts.

    Args
    ----------
    desc : dict
        A dictionary with at least the keys ``name``, ``description`` and ``args``—
        typically produced by :func:`load_tool_descs`.

    Returns
    -------
    str
        A ready-to-inject markdown block, e.g. ::

            - `web_search` : {"query": {"type": "string"}}
              Search the Web and return the top-k results.
    """
    args_json = json.dumps(desc["args"], ensure_ascii=False)
    return f"- `{desc['name']}` : {args_json}\n{desc['description']}"

def export_tool_desc(tool, kind: Literal["common", "special"]) -> None:
    """
    Dump tool metadata to ``DESC_DIR/<tool-name>.yaml``.

    The file is (re)written only if the contents have changed in order
    to avoid unnecessary disk I/O.

    Args
    ----------
    tool : Any
        A LangChain Tool instance *or* a special-tool class that exposes
        ``name``, ``description`` and ``args_schema`` attributes.
    kind : {"common", "special"}
        Category flag used later when prompts are built.
    """
    schema = (
        tool.args_schema.model_json_schema()["properties"]
        if kind == "common"
        else tool.args_schema
    )

    payload = {
        "name": tool.name,
        "description": inspect.cleandoc(tool.description or ""),
        "args": schema,
        "kind": kind,
    }

    yml_path = DESC_DIR / f"{tool.name}.yaml"
    if not yml_path.exists() or yaml.safe_load(yml_path.read_text()) != payload:
        yml_path.write_text(
            yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8"
        )

def load_tool_descs() -> List[Dict[str, Any]]:
    """
    Read every ``*.yaml`` file in :data:`agent.path.DESC_DIR`.

    Returns
    -------
    list[dict]
        A list of tool-metadata dictionaries, one per YAML file.
    """
    return [
        yaml.safe_load(p.read_text(encoding="utf-8"))
        for p in Path(DESC_DIR).glob("*.yaml")
    ]


# --------------------------------------------------------------------------- #
# Embedding model related
# --------------------------------------------------------------------------- #
def preload_embedding_model():
    pass


# --------------------------------------------------------------------------- #
# Chat memory related
# --------------------------------------------------------------------------- #
def save_chat_memory(data: List) -> None:
    """
    Persist chat memory to ``MEMORY_DIR/chat_memory.yaml`` in a human-readable form.

    Args
    ----------
    data : list
        A list of messages to serialize with PyYAML.
    """
    with open(MEMORY_DIR / "chat_memory.yaml", "w", encoding="utf-8") as fh:
        yaml.dump(
            data,
            fh,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

def load_chat_memory() -> Any:
    """
    Load chat memory previously saved by :func:`save_chat_memory`.

    Returns
    -------
    Any
        The deserialized Python object, or ``None`` if the file is missing.
    """
    path = MEMORY_DIR / "chat_memory.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
