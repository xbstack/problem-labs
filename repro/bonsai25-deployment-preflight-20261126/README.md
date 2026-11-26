# Bonsai 2.5 27B: metadata-only deployment preflight

Recorded 2026-11-26. This is an XBSTACK deployment research asset, **not a model inference benchmark**. No model weights were downloaded, no inference engine installed, and no paid endpoint called.

Run using Python 3.10+ standard library:

```bash
python3 audit.py
python3 check_inference_routes.py
```

Network requests are limited to public metadata/configuration, small source documents and two read-only loopback inventory requests (Ollama / LM Studio). The script does not run a local inference engine, start a service, load a browser demo or send a prompt. The loopback inventory probe reports only whether the exact version is present; unrelated model names are excluded. Live API responses can change. The checked-in JSON captures the original observation; copy it elsewhere before rerunning if you need to preserve that historical observation.

## Recorded observations

- Official GGUF revision: `28a7093cc25bc151cc2b284c5570f12ce343fdcf`. Eight actual artifact lengths are in result.json. File hashes are reported by the hosting API, not independently recomputed from weights.
- PTQ1_0: 5,993,834,848 bytes; PQ2_0: 7,253,354,848; Q2_0: 7,673,194,848.
- The public Qwen3.8-27B base configuration contains 16 full-attention layers, 4 KV heads, dimension 256. One sequence, FP16 K/V, unchanged base architecture, no alignment or quantization: 65,536 bytes/token; 32K → 2 GiB; 262144 → 16 GiB of **full-attention KV payload only**. This omits linear recurrent state, allocator, runtime, OS, working buffers, vision and concurrency. These are calculated sizes, not measured peaks.
- Twelve lightweight assertions pass, including exhaustive round-trip and uniqueness of all 243 five-trit tuples in a teaching codec. The codec is not the actual PTQ1_0 kernel. Three real base artifacts and MTP/vision file relationships were checked against hosting metadata.
- The homepage-linked WebGPU demo source identified Bonsai 2, not 2.5, and has browser-local loading. An older hosted demo also references an older model. Both current GGUF and MLX inference-provider mappings were empty when checked. No verified free exact-version endpoint was found within the checked routes. This is not evidence that no other service exists.
- No task accuracy, model generation speed, live RAM/VRAM, actual native engine compatibility or quality result is claimed.

## Sources

- https://prismml.com/news/bonsai-2-5-27b
- https://huggingface.co/prism-ml/Ternary-Bonsai-2.5-27B-GGUF/tree/28a7093cc25bc151cc2b284c5570f12ce343fdcf
- https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/config.json
- https://huggingface.co/prism-ml/Ternary-Bonsai-2.5-27B-mlx-2bit
- https://huggingface.co/spaces/webml-community/ternary-bonsai-2-webgpu-kernels/tree/main
- https://github.com/PrismML-Eng/Bonsai-demo

The original [XBSTACK local-model deployment guide](https://www.xbstack.com/en/ai/lfm2-5-24b-a2b-mac-memory-gguf-mlx/?utm_source=github&utm_medium=referral&utm_campaign=lfm25_mac_preflight&utm_content=bonsai25_preflight) discusses a separate MoE deployment problem. The Bonsai 2.5 editorial draft is not a published URL; we intentionally do not link to it before approval.
