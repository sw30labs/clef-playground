# Third-party notices

`vendor/clef_mlx.py` is an unchanged copy of the custom Clef MLX adapter from
[mlx-community/clef-8bit](https://huggingface.co/mlx-community/clef-8bit), licensed
under Apache-2.0 according to the upstream model card.

- Revision: `ffcdb6132b3cc94e523860321dd9ed58bc1ee9a1`
- Source: https://huggingface.co/mlx-community/clef-8bit/blob/ffcdb6132b3cc94e523860321dd9ed58bc1ee9a1/clef_mlx.py
- SHA256: `852223c944819a32fad5cf798d9d1dff30419820eaf5ad1f10cb9698afec97d5`
- The upstream license, including its existing attribution, is reproduced unchanged
  in `vendor/LICENSE`.

The model is derived from [Cloudflare/Clef](https://huggingface.co/Cloudflare/clef).
Weights are not distributed by this repository. `download_model.py` retrieves the
pinned community conversion directly from Hugging Face, including its model card
and license. The original joint schema head is retained in BF16; the backbone is
quantized to 8-bit.
