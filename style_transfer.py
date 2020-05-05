import argparse
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image

import net
from function import adaptive_instance_normalization, coral


def test_transform(size, crop):
    transform_list = []
    if size != 0:
        transform_list.append(transforms.Resize(size))
    if crop:
        transform_list.append(transforms.CenterCrop(size))
    transform_list.append(transforms.ToTensor())
    transform = transforms.Compose(transform_list)
    return transform


def style_transfer(vgg, decoder, content, style, alpha=1.0,
                   interpolation_weights=None):
    assert (0.0 <= alpha <= 1.0)
    content_f = vgg(content)
    style_f = vgg(style)
    if interpolation_weights:
        _, C, H, W = content_f.size()
        feat = torch.FloatTensor(1, C, H, W).zero_().to(device)
        base_feat = adaptive_instance_normalization(content_f, style_f)
        for i, w in enumerate(interpolation_weights):
            feat = feat + w * base_feat[i:i + 1]
        content_f = content_f[0:1]
    else:
        feat = adaptive_instance_normalization(content_f, style_f)
    feat = feat * alpha + content_f * (1 - alpha)
    return decoder(feat)

def main_func(content_path, style_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    content_path = Path(content_path)
    style_path = Path(style_path)
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True, parents=True)
    do_interpolation = False
    decoder = net.decoder
    vgg = net.vgg

    decoder.eval()
    vgg.eval()

    decoder.load_state_dict(torch.load('models/decoder.pth'))
    vgg.load_state_dict(torch.load('models/vgg_normalised.pth'))
    vgg = nn.Sequential(*list(vgg.children())[:31])

    vgg.to(device)
    decoder.to(device)

    content_size = 1024
    style_size = 500
    crop = True
    preserve_color = False
    alpha = 1.0
    interpolation_weights = [0.3, 0.7]

    content_tf = test_transform(content_size, crop)
    style_tf = test_transform(style_size, crop)

    if do_interpolation:  # one content image, N style image
        style = torch.stack([style_tf(Image.open(str(p))) for p in style_paths])
        content = content_tf(Image.open(str(content_path))) \
            .unsqueeze(0).expand_as(style)
        style = style.to(device)
        content = content.to(device)
        with torch.no_grad():
            output = style_transfer(vgg, decoder, content, style,
                                    alpha, interpolation_weights)
        output = output.cpu()

    else:  # process one content and one style
        content = content_tf(Image.open(str(content_path)))
        style = style_tf(Image.open(str(style_path)))
        if preserve_color:
            style = coral(style, content)
        style = style.to(device).unsqueeze(0)
        content = content.to(device).unsqueeze(0)
        with torch.no_grad():
            output = style_transfer(vgg, decoder, content, style,
                                    alpha)
        output = output.cpu()

        output_name = output_dir / '{:s}_stylized_{:s}_alpha_{:s}{:s}'.format(
                    content_path.stem, style_path.stem, str(alpha), '.jpg')
        save_image(output, str(output_name))

    return output_name




