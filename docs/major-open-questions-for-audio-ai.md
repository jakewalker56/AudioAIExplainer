
## Major open questions for Audio LLMs
Tokenizers
Continuous distributions / soft-tokens vs. discrtete values / hard tokens (from Wavenet paper - "However, van den Oord et al. (2016a) showed that a softmax distribution tends to work better, even when the data is implicitly continuous (as is the case for image pixel intensities or audio sample values). One of the reasons is that a categorical distribution is more flexible and can more easily model arbitrary distributions because it makes no assumptions about their shape.")
Model architecture (side channeling information like speaker identity)
Cross-modal generalization vs. specialization
Diffusion vs. autoregressive token prediction
Fine tuning vs. LoRA vs. shoving history in context prompt window (e.g. RAG)
Zero and few shot tuning / data efficiency / new algorithms needed
Multichannel audio tokenizers - model audio sources independently, use spacial information to bias model toward more likely speaker targets; model audio as "speech and non-speech" where the tokenizer is doing implicit speech separation; represent non-speech audio with different tokens than used for speech audio;  Use both low-fidelity speech tokens and high fidelity acoustic tokens as input, but only output the speech tokens and use audio synthesizer to fill in the acoustic gaps
Channel separated training data
Non-reconstructive speech tokenizers - explicitly get rid of background noise, channel effects, acoustic enviornment, and even speaker information; just model the semantics of the input speech.  Basically an ASR tokenizer that also captures prosody, not just lexical units; from an information theorteic POV, non-speaker-and-channel-independent tokenizers is equivalent training a text model where every webpage is a different language.  You're asking the model to first implicitly learn a speaker-and-channel-independent representation to operate on, making it job way way harder.
Pushing boundaries of synthetic data + data augumentation - don't have a good understanding of text data, but seems like adding math and science data can meaningfully change model performance for text; most training data is from very specific acoustic environment


https://sebastianraschka.com/blog/2025/from-gpt-2-to-gpt-oss.html

Supervised fine tuning vs. RL HF - what is the difference and why might one work better and in which case? - https://www.reddit.com/r/MachineLearning/comments/1mnfoum/d_has_anyone_tried_crossmodal_transfer_for_visual/

Chain of thought
Full duplex models

State space models - https://arxiv.org/abs/2111.00396
WavChat - survey of speech llm models https://arxiv.org/pdf/2411.13577
SpeechTokenizer - https://github.com/ZhangXInFD/SpeechTokenizer/?tab=readme-ov-file
SpeechTrident survey - https://github.com/ga642381/speech-trident/
On the landscape of spoken language models - https://arxiv.org/pdf/2504.08528
Audio token taxonomy - https://poonehmousavi.github.io/dates-website/taxonomy

-Suno / MusicLM / Song DJ (Googles's music LM thing that launched?)
-ElevenLabs audio effect generation API
-TokenSplit / Universal Sound Separation / Audio Magic Eraser
