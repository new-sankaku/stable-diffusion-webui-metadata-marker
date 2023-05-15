import modules.scripts as scripts
import gradio as gr
import os

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin, ImageOps
from modules import images, script_callbacks
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state
from datetime import datetime
import modules.shared as shared
import png
import io
import numpy


class MetadataMarkerScript(scripts.Script):

    def title(self):
        return "Extension Template"

    # Decide to show menu in txt2img or img2img
    # - in "txt2img" -> is_img2img is `False`
    # - in "img2img" -> is_img2img is `True`
    #
    # below code always show extension menu
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    # Setup menu ui detail
    def ui(self, is_img2img):
        with gr.Accordion('Metadata Marker', open=False):
            with gr.Row():
                output_image_checkbox = gr.Checkbox(
                    False,
                    label="Output Image Enabled"
                )
            with gr.Row():
                prompt_checkbox = gr.Checkbox(
                    True,
                    label="Prompt"
                )
                negative_prompt_checkbox = gr.Checkbox(
                    True,
                    label="Negative prompt"
                )
                steps_checkbox = gr.Checkbox(
                    True,
                    label="Steps"
                )
                sampler_checkbox = gr.Checkbox(
                    True,
                    label="Sampler"
                )
            with gr.Row():
                cfg_scale_checkbox = gr.Checkbox(
                    True,
                    label="CFG scale"
                )
                seed_checkbox = gr.Checkbox(
                    True,
                    label="Seed"
                )
                size_checkbox = gr.Checkbox(
                    True,
                    label="Size"
                )
                model_checkbox = gr.Checkbox(
                    True,
                    label="Model"
                )
                model_hash_checkbox = gr.Checkbox(
                    True,
                    label="Model hash"
                )
            with gr.Row():
                meta_data_display = gr.inputs.Dropdown(label="MetaData Display Position", choices=["Overlay", "Top", "Bottom", "Left", "Right"], default="Overlay")
                font_size_input = gr.inputs.Textbox(lines=1, label='Font Size', default="")
    
        return [prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                sampler_checkbox, cfg_scale_checkbox, seed_checkbox, 
                size_checkbox, model_checkbox, model_hash_checkbox, 
                output_image_checkbox, meta_data_display, font_size_input]
    






    #p  is StableDiffusionProcessing
    #pp is PostprocessImageArgs
    # The original function now calls the new functions for each task
    def postprocess_image(self, p, pp, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                          sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, output_image_checkbox, meta_data_display,
                          font_size_input):
    
        if not output_image_checkbox:
            return;
    
        stream = io.BytesIO()
        pp.image.save(stream, format="PNG")
        stream_copy = io.BytesIO(stream.getvalue())
        image_copy = Image.open(stream_copy)
        
        draw = ImageDraw.Draw(image_copy)
        
        font_path = self.get_font_path()
        imageSize = image_copy.width * image_copy.height
        fontSize = self.get_font_size(imageSize, font_size_input)

        font = self.get_font(font_path, fontSize)
        
        text = self.construct_text(p, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                                   sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, 
                                   model_checkbox, model_hash_checkbox, shared)
        
        max_width = image_copy.width
        text, linesize, max_line_length = self.wrap_text(text, max_width, font, draw)
        font_width, font_height = draw.textsize("A", font=font)
    
        text_width, text_height = draw.textsize(text, font=font)
        
        text_height = text_height + font_height
        
        x = 0
        y = image_copy.height - text_height
        
        x_plus = 0
        y_plus = 0
        
        insufficient_height = text_height - image_copy.height
        if insufficient_height < 0:
            insufficient_height = 0
        
        if meta_data_display == "Top":
            image_copy = ImageOps.expand(image_copy, border=(0, text_height, 0, 0), fill='white')
            y = 0
        elif meta_data_display == "Bottom":
            image_copy = ImageOps.expand(image_copy, border=(0, 0, 0, text_height), fill='white')
            y_plus = text_height
        elif meta_data_display == "Left":
            image_copy = ImageOps.expand(image_copy, border=(text_width, 0, 0, insufficient_height), fill='white')
            y = 0
        elif meta_data_display == "Right":
            image_copy = ImageOps.expand(image_copy, border=(0, 0, text_width, insufficient_height), fill='white')
            x_plus = text_width
            x = image_copy.width - text_width
            y = 0
        
        text_image = Image.new('RGBA', image_copy.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_image)

        print()
        print("max_line_length:" + str(max_line_length))
        
        
        print("text_width:" + str(text_width))
        print("text_height:" + str(text_height))
        
        print("x1:" + str(x))
        print("y1:" + str(y))
        print("x2:" + str((x + text_width)))
        print("y2:" + str((y + text_height)))
        
        if meta_data_display == "Overlay":
            draw.rectangle((x, y, x + text_width, y + text_height), fill=(255, 255, 255, 180))
        
        
        draw.text((x, y+y_plus), text, fill='black', font=font)

        image_copy = Image.alpha_composite(image_copy.convert('RGBA'), text_image)
    
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d%H%M%S%f")
        image_copy.save(f'{p.outpath_samples}/metadata_{timestamp_str}.png', format="PNG")

    # Function to get font path based on OS
    def get_font_path(self):
        if os.name == 'nt':  # Windows
            font_path = 'C:\\Windows\\Fonts\\meiryo.ttc'
        elif os.name == 'posix':  # Linux
            font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        else:  # Mac
            font_path = '/System/Library/Fonts/Hiragino Sans Rounded W4.ttc'
        return font_path
    
    
    
    def check_input(self, input_value):
        if not input_value.isdigit():
            print("Invalid input font size: Only numeric values are allowed. Set automatically.!!")
            return 0
        else:
            return int(input_value)

    # Function to get font size based on image size
    def get_font_size(self, imageSize, font_size_input):

        font_size_value = self.check_input(font_size_input)

        if font_size_value != 0:
            return font_size_value

        fontSize = 13
        if (512*512 > imageSize):
            fontSize = 11
        elif (728*728 > imageSize):
            fontSize = 13
        elif ( 850*850 > imageSize ):
            fontSize = 16
        elif ( 1000*1000 > imageSize ):
            fontSize = 19
        elif ( 1200*1200 > imageSize ):
            fontSize = 22
        elif ( 1500*1500 > imageSize ):
            fontSize = 25
        else:
            fontSize = 28
        return fontSize

    
    # Function to get font object
    def get_font(self, font_path, fontSize):
        if not os.path.isfile(font_path):
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, fontSize)
        return font
    
    # Function to construct the text string based on checkboxes
    def construct_text(self, p, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                          sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, shared):
        first_text = ""
        if prompt_checkbox:
            first_text = first_text + "Prompt: " + str(p.prompt) + "\n\n"

        if negative_prompt_checkbox:
            first_text = first_text + "Negative prompt: " + str(p.negative_prompt)

        second_text = ""
        if steps_checkbox:
            second_text = second_text + ", Steps: " + str(p.steps)
            
        if sampler_checkbox:
            second_text = second_text + ", Sampler: " + str(p.sampler_name)
        
        if cfg_scale_checkbox:
            second_text = second_text + ", CFG scale: " + str(p.cfg_scale)
        
        if seed_checkbox:
            second_text = second_text + ", Seed: " + str(p.seed)
        
        if size_checkbox:
            second_text = second_text + ", Size: " + str(p.width) + "x" + str(p.height)

        if model_hash_checkbox:
            second_text = second_text + ", Model hash: " + str( shared.sd_model.sd_model_hash )
            
        if model_checkbox:
            second_text = second_text + ", Model : " + str(shared.sd_model.sd_checkpoint_info.model_name)
        
        first_text = first_text.strip()
        first_text = first_text.strip()
        
        second_text = second_text.strip()
        second_text = second_text.strip(",")
        second_text = second_text.strip()
        
        if(first_text != "" and second_text != ""):
            return first_text + "\n\n" + second_text
        else:
            return first_text + second_text
    
    def wrap_text(self, text, max_width, font, draw):
        lines = []
        line = ""
        max_line_length = 0 
        
        for char in text:
            temp_line = line + char
            temp_width, temp_height = draw.textsize(temp_line, font=font)
    
            if char == '\n' or char == '\r\n':
                lines.append(line)
                line = ""
            elif temp_width < max_width:
                line = temp_line
            else:
                lines.append(line)
                if len(line) > max_line_length: 
                    max_line_length = len(line)
                line = char
    
        lines.append(line)
        if len(line) > max_line_length: 
            max_line_length = len(line)
    
        # リストの長さ（行の数）を取得
        num_lines = len(lines)
        
        return "\n".join(lines), num_lines, max_line_length 

    
