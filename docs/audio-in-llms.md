# Audio in LLMs
### wavenet
Receptive field of 300ms
Output values quantiezed to 256 (non-linear) possible values, allows for softmax loss function
At least 2 interpretations:
1) With unconditional sampling, this is just autoregressive token generation where the token codebook is very small (256) and the token width is very small (1/16000 seconds, or ~0.06ms) and produces realistic sounding gibberish (same as early AudioLM experiments)
2) With conditional sampling, this is just a neural vocoder (you feed it high level sequence features like phonemes, linguistic features, or even spectrogram features, and it produces audio waveform sample values)
What would you get if you replaced the CNN backbone with a big transformer?

## LLMs
Transformers (cross-attention, scale, benefits vs. LSTM / RNNs, scale scale scale)
ChatGPT - Generative Pretrained Transformer
Autoregressive token prediction
Encoder-only vs. Encoder-decoder models
Sampling methodology (temperature, top-k sampling, greedy sampling)
Tokenizers and how they impact performance (capital vs. lowercase letters, sequences of numbers / math, number of r's in strawberry)
Discrete vs. continuous output (cross entropy loss, modeling fundamentally tokenized data (sort of, given first thing transformer does is project tokens into continuous space))
Note: no time component! fundamentally different from audiovisual data

## Tokens
W2Vec embeddings
### Wav2Vec & Wav2Vec 2.0
### Wave2Vec-BERT 
### BEST-RQ
OpenAI tokenizer link


## Audio LLMs

## Audio Tokenizers
Wav2Vec
w2v-bert
Spectrograms
Soundstream (RVQ)
Moshi tokenizer
Microsoft tokenizer

What is the scale of the information you are trying to model? (for speech generation, you care about the words and the prosody; for audio synthesizer you care about the phase information and fine acoustic details and speaker voice characteristics.  Hierarchical modeling is the obvious way to solve this - but how do you implement it?  acoustic and semantic tokens (plus depthformer) like audiolm?  Heirarchical transformers like Moshi?  Multi-timescale hierarchical tokens like prosody tokens from Aren?  Jointly modeling acoustic and sematnics from same underlying latent, or model them separately?  Jake's thesis: you will get significantly better semantic quality from multimodal LLM output if you find better ways to isolate the semantic information you're trying to model (which is mostly high level word / phoneme / prosody) and treat the synthesis part as a generative task conditioned on semantic representation a la diffusion.  ASR tokens are a TERRIBLE idea for generation.)  Annotated text vs. prosody tokens - the bitter lesson implies we shouldn't work on hand designed features, but rather let the machine learn which features are important.  Prosody tokens > annotations.

AudioLM
Tortise-TTS (ElevenLabs)

## Audio-enabled multimodel LLMs
AudioPaLM
ChatGPT
Gemini
Veo3
Sesame Labs (/ Maya? Apparently Johan contributed to that too)
Streaming / full duplex
Moshi model- https://github.com/kyutai-labs/moshi
Facebook superintelligence lab?
Lab that Miana went to after Google

