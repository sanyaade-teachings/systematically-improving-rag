-- Pandoc Lua filter to convert Mermaid diagrams to images
-- Requires mermaid-cli (mmdc) to be installed

local system = require 'pandoc.system'
local utils = require 'pandoc.utils'
local path = require 'pandoc.path'

local function file_exists(name)
  local f = io.open(name, "r")
  if f ~= nil then
    io.close(f)
    return true
  else
    return false
  end
end

local function mermaid_to_image(code, filetype, outdir)
  -- Create output directory if it doesn't exist
  system.make_directory(outdir, true)
  
  -- Generate unique filename based on content hash
  local hash = utils.sha1(code)
  local basename = "mermaid-" .. hash
  local mmd_file = path.join({outdir, basename .. ".mmd"})
  local img_file = path.join({outdir, basename .. "." .. filetype})
  
  -- Check if image already exists
  if file_exists(img_file) then
    return img_file
  end
  
  -- Write mermaid code to temporary file
  local f = io.open(mmd_file, "w")
  if not f then
    io.stderr:write("Error: Could not create temporary file " .. mmd_file .. "\n")
    return nil
  end
  f:write(code)
  f:close()
  
  -- Convert to image using mermaid-cli with custom config
  local config_file = "scripts/mermaid-config.json"
  local cmd = string.format('mmdc -i "%s" -o "%s" -c "%s" -b white --scale 2 --width 800', 
                           mmd_file, img_file, config_file)
  
  local success = os.execute(cmd)
  
  -- Clean up temporary file
  os.remove(mmd_file)
  
  if success == 0 and file_exists(img_file) then
    return img_file
  else
    io.stderr:write("Warning: Failed to convert Mermaid diagram\n")
    return nil
  end
end

function CodeBlock(block)
  -- Check if this is a mermaid code block
  if block.classes and block.classes[1] == "mermaid" then
    local outdir = "images"
    local filetype = "png"
    
    -- Try to convert to image
    local img_path = mermaid_to_image(block.text, filetype, outdir)
    
    if img_path then
      -- Return an image element
      return pandoc.Para({
        pandoc.Image({}, img_path, "", {alt = "Mermaid diagram"})
      })
    else
      -- Fallback: return as regular code block with warning
      local warning = pandoc.Para({
        pandoc.Emph({pandoc.Str("Warning: Could not render Mermaid diagram")})
      })
      return {warning, block}
    end
  end
  
  -- Return unchanged if not a mermaid block
  return block
end
