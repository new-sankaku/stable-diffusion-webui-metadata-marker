import modules.scripts as scripts
import gradio as gr
import os
import subprocess
import modules.shared as shared
import png
import io
import numpy
import matplotlib.font_manager

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin, ImageOps
from modules import images, script_callbacks
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state
from datetime import datetime

class MetadataMarkerScript(scripts.Script):

    start_time = None

    def __init__(self):
        self.start_time = None

    def title(self):
        return "Extension Metadata Marker"

    # Decide to show menu in txt2img or img2img
    # - in "txt2img" -> is_img2img is `False`
    # - in "img2img" -> is_img2img is `True`
    #
    # below code always show extension menu
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def process(self, p, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                          sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, output_image_checkbox, meta_data_display,
                          font_size_input, font_choice, opacity_slider, font_color, background_color, footer_text_area, system_infomation_checkbox):
        self.start_time = datetime.now()
        
        
    
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
            with gr.Row():
                sampler_checkbox = gr.Checkbox(
                    True,
                    label="Sampler"
                )
                cfg_scale_checkbox = gr.Checkbox(
                    True,
                    label="CFG scale"
                )
                seed_checkbox = gr.Checkbox(
                    True,
                    label="Seed"
                )
            with gr.Row():
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
                system_infomation_checkbox = gr.Checkbox(
                    True,
                    label="System Information"
                )
            
            with gr.Row():
                meta_data_display = gr.inputs.Dropdown(label="MetaData Display Position", choices=["Overlay", "Overlay Center", "Top", "Bottom", "Left", "Right"], default="Overlay")

                font_size_input = gr.inputs.Textbox(lines=1, label='Font Size', default="")
                
                fonts_list = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
                fonts_dict = {os.path.splitext(os.path.basename(font))[0]: font for font in fonts_list}
                font_choice = gr.inputs.Dropdown(choices=sorted(list(fonts_dict.keys())), label='Font Choice')
                
            with gr.Row():
                font_color = gr.ColorPicker(value="#000000", label="font color")
                background_color = gr.ColorPicker(value="#FFFFFF", label="background color")
                opacity_slider = gr.inputs.Slider(minimum=0, maximum=255, default=180, label='Opacity')

            with gr.Row():
                footer_text_area = gr.inputs.Textbox(lines=4, label='footer text')
                
                return [prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                        sampler_checkbox, cfg_scale_checkbox, seed_checkbox, 
                        size_checkbox, model_checkbox, model_hash_checkbox, 
                        output_image_checkbox, meta_data_display, font_size_input, 
                        font_choice, opacity_slider, font_color, background_color, footer_text_area, system_infomation_checkbox]
    






    #p  is StableDiffusionProcessing
    #pp is PostprocessImageArgs
    # The original function now calls the new functions for each task
    def postprocess_image(self, p, pp, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                          sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, output_image_checkbox, meta_data_display,
                          font_size_input, font_choice, opacity_slider, font_color, background_color, footer_text_area, system_infomation_checkbox):

        if not output_image_checkbox:
            return;
        
        
        
        
        stream = io.BytesIO()
        pp.image.save(stream, format="PNG")
        stream_copy = io.BytesIO(stream.getvalue())
        image_copy = Image.open(stream_copy)
        
        draw = ImageDraw.Draw(image_copy)
        
        if not font_choice:
            selected_font_path = self.get_font_path()
        else:
            fonts_list = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
            fonts_dict = {os.path.splitext(os.path.basename(font))[0]: font for font in fonts_list}
            selected_font_path = fonts_dict[font_choice]
        
        imageSize = image_copy.width * image_copy.height
        fontSize = self.get_font_size(imageSize, font_size_input)
        font = self.get_font(selected_font_path, fontSize)
        text = self.construct_text(p, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, 
                                   sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, 
                                   model_checkbox, model_hash_checkbox, system_infomation_checkbox, shared)
        
        max_width = image_copy.width
        max_height = image_copy.height
        
        text = text + "\n\n" + footer_text_area 
        text = text.strip()
        text = text.strip()
        
        large_size = 0
        if image_copy.width > image_copy.height :
            large_size = image_copy.width
        else :
            large_size = image_copy.height
        
        
        if meta_data_display == "Left" or meta_data_display == "Right":
            large_size = large_size/2 
        else:
            large_size = large_size = image_copy.width
        
        text, linesize, max_line_length = self.wrap_text(text, large_size, font, draw)
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
        
        background_color_rgba = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (opacity_slider,)
        font_color_rgba = tuple(int(font_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        
        if meta_data_display == "Top":
            image_copy = ImageOps.expand(image_copy, border=(0, text_height, 0, 0), fill=background_color_rgba)
            y = 0
        elif meta_data_display == "Bottom":
            image_copy = ImageOps.expand(image_copy, border=(0, 0, 0, text_height), fill=background_color_rgba)
            y_plus = text_height
        elif meta_data_display == "Left":
            image_copy = ImageOps.expand(image_copy, border=(text_width, 0, 0, insufficient_height), fill=background_color_rgba)
            y = 0
        elif meta_data_display == "Right":
            image_copy = ImageOps.expand(image_copy, border=(0, 0, text_width, insufficient_height), fill=background_color_rgba)
            x_plus = text_width
            x = image_copy.width - text_width
            y = 0
        
        text_image = Image.new('RGBA', image_copy.size, (255, 255, 255, 0), )
        draw = ImageDraw.Draw(text_image)
        
        if meta_data_display == "Overlay":
            draw.rectangle((x, y, max_width, max_height), fill=background_color_rgba)
            
        if meta_data_display == "Overlay Center":
            x = 0
            y = (image_copy.height - text_height ) / 2
            draw.rectangle((x, y, max_width, (y+text_height) ), fill=background_color_rgba)
            lines = text.split("\n")
            line_height = font.getsize("hg")[1]  # 行の高さを取得
            
            text_height = line_height * len(lines)  # テキスト全体の高さを計算
            
            y = (image_copy.height - text_height) // 2
            
            for line in lines:
                line_width, line_height = draw.textsize(line, font=font)
                x = (image_copy.width - line_width) // 2
                draw.text((x, y), line, fill=font_color_rgba, font=font)
                y += line_height  # 次の行に移動        
        else:
            draw.text((x, y+y_plus), text, fill=font_color_rgba, font=font)

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
                          sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, system_infomation_checkbox, shared):
        end_time = datetime.now()
        
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
            second_text = second_text + ", Model: " + str(shared.sd_model.sd_checkpoint_info.model_name)
        
        third_text = ""
        if system_infomation_checkbox:
            gpu_info = self.get_gpu_info()
            if gpu_info:
                output_string = '\n'.join([f'GPU: {x[0]}, Total: {x[1]}MB' for x in gpu_info])
            else:
                output_string = 'GPU unknown'
                
            third_text = third_text + ", " + output_string
            time_difference = self.calculate_time_difference(self.start_time, end_time)
            third_text = third_text + ", Time taken: " + str(time_difference) + "s, "
        
        first_text = first_text.strip()
        first_text = first_text.strip()
        
        second_text = second_text.strip()
        second_text = second_text.strip(",")
        second_text = second_text.strip()
        
        third_text = third_text.strip()
        third_text = third_text.strip(",")
        third_text = third_text.strip()
        
        resultText = ""
        if(first_text != ""):
            resultText = first_text
            
        if(second_text != "" and resultText != ""):
            resultText = resultText + "\n" + second_text
        elif(second_text != ""):
            resultText = second_text
            
        if(third_text != "" and resultText != ""):
            resultText = resultText + "\n" + third_text
        elif(third_text != ""):
            resultText = third_text
        
        return resultText

    def calculate_time_difference(self, start_time, end_time):
        time_difference = end_time - self.start_time 
        seconds = round(time_difference.total_seconds(), 1)
        return seconds
    
    def get_gpu_info(self):
        _output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
    
        COMMAND = "nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free --format=csv,noheader"
    
        try:
            gpu_output = _output_to_list(subprocess.check_output(COMMAND.split()))
            gpu_output = [x.split(',') for x in gpu_output]
            gpu_info = []
            for x in gpu_output:
                name = x[0]
                total_memory = int(x[1].split()[0])
                used_memory = int(x[2].split()[0])
                free_memory = int(x[3].split()[0])
                gpu_info.append((name, total_memory, used_memory, free_memory))
        except (subprocess.CalledProcessError, FileNotFoundError):
            gpu_info = []  # エラー時は空のリストを返す
    
        return gpu_info
        
    def add_line(self, line, line_list, max_line_length, update_max_length=True):
        if line:  # Check if line is not empty
            line_list.append(line)
            if update_max_length and len(line) > max_line_length:
                max_line_length = len(line)
        return "", max_line_length
    
    def check_width(self, line, word, space_separated, max_width, font, draw):
        if space_separated and line:
            temp_line = f"{line} {word}"
        else:
            temp_line = f"{line}{word}"
        temp_width, _ = draw.textsize(temp_line, font=font)
        return temp_line if temp_width <= max_width else None
    
    def word_to_char(self, line, word, lines, max_line_length, max_width, font, draw):
        for char in word:
            temp_line = self.check_width(line, char, False, max_width, font, draw)
            if temp_line:
                line = temp_line
            else:
                line, max_line_length = self.add_line(line, lines, max_line_length, update_max_length=False)
                line += char
        return line, max_line_length
    
    def wrap_text(self, text, max_width, font, draw):
        paragraphs = text.split('\n')
        lines = []
        max_line_length = 0
        double_newline = False  # 追加: 2行続きの改行を保持するフラグ
    
        for paragraph in paragraphs:
            space_separated = ' ' in paragraph
            words = paragraph.split() if space_separated else list(paragraph)
            line = ""
            for word in words:
                temp_line = self.check_width(line, word, space_separated, max_width, font, draw)
                if temp_line:
                    line = temp_line
                else:
                    line, max_line_length = self.add_line(line, lines, max_line_length)
                    temp_line = self.check_width(line, word, space_separated, max_width, font, draw)
                    if temp_line:
                        line = temp_line
                    else:
                        line, max_line_length = self.word_to_char(line, word, lines, max_line_length, max_width, font, draw)
    
            if line:  # Check if line is not empty before adding
                line, max_line_length = self.add_line(line, lines, max_line_length)
                if double_newline:  # 追加: 2行続きの改行を保持する場合
                    lines.append("")  # 空行を追加
                    double_newline = False
            elif not double_newline:  # 追加: 空行が続いていない場合
                lines.append("")  # 空行を追加
                double_newline = True  # 2行続きの改行を保持するフラグを立てる
    
        num_lines = len(lines)
        return "\n".join(lines), num_lines, max_line_length


