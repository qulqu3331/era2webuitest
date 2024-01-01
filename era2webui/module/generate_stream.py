import torch
import threading
from diffusers import AutoencoderTiny, StableDiffusionPipeline
from streamdiffusion import StreamDiffusion
from streamdiffusion.image_utils import postprocess_image

class ImageGenerator:
    _instance = None

    @classmethod #インスタンスがNoneでも動くために必要なデコレータ
    def get_instance(cls):
        """インスタンス作成メソッド
        既存のインスタンスがあればそれを返す
        これをやらないと生成ごとにモデルロードする
        Returns:
            _type_: _description_
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # モデルと設定の初期化
        self.pipe = StableDiffusionPipeline.from_pretrained("KBlueLeaf/kohaku-v2.1").to(
            device=torch.device("cuda"),
            dtype=torch.float16,
        )

        # Diffusers pipelineをStreamDiffusionにラップ
        self.stream = StreamDiffusion(
            self.pipe,
            t_index_list=[0, 16, 32, 45],
            torch_dtype=torch.float16,
            cfg_type="none",
        )

        # モデルがLCMでなければマージする
        self.stream.load_lcm_lora()
        self.stream.fuse_lora()
        # Tiny VAEで高速化
        self.stream.vae = AutoencoderTiny.from_pretrained("madebyollin/taesd").to(
            device=self.pipe.device, dtype=self.pipe.dtype
        )
        # xformersで高速化
        self.pipe.enable_xformers_memory_efficient_attention()

    def generate_image(self, prompt):
        # streamを準備する
        self.stream.prepare(prompt)

        # Warmup >= len(t_index_list) x frame_buffer_size
        for _ in range(4):
            self.stream()

        # 画像を生成して表示
        x_output = self.stream.txt2img()
        thread = threading.Thread(target=self.show_image, args=(x_output,))
        thread.start()

        return 200

    def show_image(self, x_output):
        image = postprocess_image(x_output, output_type="pil")[0]
        image.show()