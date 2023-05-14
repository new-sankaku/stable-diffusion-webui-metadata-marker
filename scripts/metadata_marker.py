import modules.scripts as scripts
import gradio as gr
import os

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
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
                
                
                
        return [prompt_checkbox, negative_prompt_checkbox, steps_checkbox, sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, output_image_checkbox]


    #p  is StableDiffusionProcessing
    #pp is PostprocessImageArgs
    def postprocess_image(self, p, pp, prompt_checkbox, negative_prompt_checkbox, steps_checkbox, sampler_checkbox, cfg_scale_checkbox, seed_checkbox, size_checkbox, model_checkbox, model_hash_checkbox, output_image_checkbox):
    
        if not output_image_checkbox:
            return;

        stream = io.BytesIO()
        pp.image.save(stream, format="PNG")
        stream_copy = io.BytesIO(stream.getvalue())
        image_copy = Image.open(stream_copy)
        
        draw = ImageDraw.Draw(image_copy)
        
        # OSに応じてフォントを選択
        font_path = None
        if os.name == 'nt':  # Windows
            font_path = 'C:\\Windows\\Fonts\\meiryo.ttc'
        elif os.name == 'posix':  # Linux
            font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        else:  # Mac
            font_path = '/System/Library/Fonts/Hiragino Sans Rounded W4.ttc'
        
        imageSize = image_copy.width * image_copy.height

        fontSize = 13;
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
        
        # フォントファイルが存在するか確認し、存在しない場合は適切なフォントにフォールバック
        if not os.path.isfile(font_path):
            # フォントファイルが存在しない場合、Pillowのデフォルトフォントを使用
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, fontSize)
        
        text = ""
        if prompt_checkbox:
            text = text + "Prompt: " + str(p.prompt)
        
        if negative_prompt_checkbox:
            text = text + ", Negative prompt: " + str(p.negative_prompt)
        
        if steps_checkbox:
            text = text + ", Steps: " + str(p.steps)
            
        if sampler_checkbox:
            text = text + ", Sampler: " + str(p.sampler_name)
        
        if cfg_scale_checkbox:
            text = text + ", CFG scale: " + str(p.cfg_scale)
        
        if seed_checkbox:
            text = text + ", Seed: " + str(p.seed)
        
        if size_checkbox:
            text = text + ", Size: " + str(p.width) + "x" + str(p.height)

        if model_hash_checkbox:
            text = text + ", Model hash: " + str( shared.sd_model.sd_model_hash )
            
        if model_checkbox:
            text = text + ", Model : " + str(shared.sd_model.sd_checkpoint_info.model_name)
        
        text = text.strip()
        

        max_width = image_copy.width
        lines = []
        line = ""
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
                line = char


        lines.append(line)
        text = "\n".join(lines)
        
        text_width, text_height = draw.textsize("AAA", font=font)
        text_image = Image.new('RGBA', image_copy.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_image)
        
        x = 0
        y = image_copy.height - (text_height * (len(lines)+2))

        print("len(lines):" + str(len(lines)) )
        print("lines height:" + str(text_height) )
        print("x1:" + str(x) )
        print("y1:" + str(y) )
        print("x2:" + str(image_copy.width) )
        print("y2:" + str(image_copy.height) )
        draw.rectangle( (x, y, image_copy.width, image_copy.height), fill=(255, 255, 255, 180))
        draw.text((x, y), text, fill='black', font=font)
        image_copy = Image.alpha_composite(image_copy.convert('RGBA'), text_image)
                
        
        now = datetime.now()
        timestamp_str = now.strftime("%Y%m%d%H%M%S%f")
        image_copy.save(f'{p.outpath_samples}/metadata_{timestamp_str}.png', format="PNG")

