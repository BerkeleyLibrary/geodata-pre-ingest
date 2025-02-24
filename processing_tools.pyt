# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from shutil import copyfile, rmtree
from create_workspace_tool import CreateWorkspaceTool
from select_workspace_tool import SelectWorkspaceTool
from prepare_batch_tool import PrepareBatchTool


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoblacklightToolbox"
        self.alias = "geoblacklight_toolbox"    
        self.tools = [CreateWorkspaceTool,SelectWorkspaceTool, PrepareBatchTool]
