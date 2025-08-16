# How Older Audio Models Work

Overview…

<div id="viz-models"></div>
<script type="py" src="py/older_models.py" config="pyscript.toml" target="#viz-models"></script>


## How Classical Audio ML Works
We've now laid the ground work for all the pieces needed to talk about how audio ML models worked before transformers / LLMs came to the forefront circa 2020.  We'll briefly discuss the tasks and models used in this period before moving on to what audio looks like in the new LLM world.

There are several ways to slice up the audio ML space.  One important axis for audio data is the *content* of the audio, which generally falls into three categores: speech, music, and open domain (aka "everything else"). Another important axis is whether the task you're trying to accomplish is an analysis task (understanding the content of the audio), a generation task (modifying or creating new audio), or a DSP task (things that are more "signal processing" than they are understanding or generation, such as dereverberation, bandwidth extension, echo cancellation, etc.) [Aside] Of course these categories are artificially discrete, and there are plenty of areas that blur these boundaries.  Even before LLMs, there were efforts at speech-to-speech translation models, speech-to-translated-text models, universal audio separation, audio removal, and other tasks that don't fit neatly into a single audio type and task category [/Aside]

Historically, specialized models were trained for individual tasks within each content type; one model for ASR, a different model for denoising, a different model for music generation, etc.  Some tasks generalize across content types (e.g. bandwidth extension), but even here it was typical to have seperate models for different content types (e.g. a "speech" bandwidth extention model that is different from the "music" bandwidth extension model).  Given this reality, it is perhaps not surprising that research in each of these areas was largely siloed - "speech" and "music" people didn't talk to each other nearly as much as you might think, and speech generation (TTS) and speech analysis (ASR) were almost entirely seperate disciplines with different conferences and different academic labs. [Aside] I have always found this somewhat scandalous. It is *beyond obvious* that speech analysis and speech generation ought to *at least* be leveraging shared representations and data even if the core modeling approaches are different.  It was not until audio was adapted into the LLM domain that this became a reality in any meaningful way, and this represents to me an enormous failure of research institutions.[/Aside]  

For the duration of this document we're going to focus almost entirely on the speech domain, but most of what we talk about will have clear parallels in music / open domain audio. 

### ASR Circa 2020

Automatic Speech Recognition (ASR) is the task of producing a transcript from a segment of audio. "Transcript" is a bit underspecified, as there are many different capabilities you may want out of an ASR model depending on the use case - some common extensions include:
- streaming models (where the transcript is produced in real time as new audio comes in)
- timing information (sentence / word / phoneme start and end times)
- multilingual support (a single model that can transcribe speech from multiple languages) 
- vocal burst support (transcribing coughing, sneezing, laughter, and other non-lexical speech-like noises)
- captioning (annotating important non-speech audio events in-line with transcription text)
- noise robustness (transcribing in the presence of background noise or channel artifacts)
- speaker turn identification (identifying in the transcript when the speaker changes, but not identifying when two segments are from the same speaker)
- multispeaker diarization (identifying which speaker is speaking at any given point in the transcript)

[Aside] In practice, even within the same "task definition" you often get multiple models that claim SOTA performance, and when you go and try them you might find one to be far superior to the other for what you're trying to do.  What's going on here is generally domain shift from the training and eval data, because all models are trained (and sometimes evaled) on data with subtley different characteristics (how noisy is the training data? What is the min / max / average volume of audio samples?  Is there overlapping speech?  Are there any recording channel artifacts like reverb, echo, etc?  What type of microphone was the data captured on?  How long are the min / max / average samples? etc.)  [/Aside]

Intuitively, there's basically two ways to do ASR: 
1) You have a model predict once every N milliseconds which phoneme it thinks is currently being verbalized in the audio, then you try to piece these predictions together into something that looks like a coherent string of words
2) You have a big black box model that processes a sequence of audio input, and it directly spits out a sequence of output phonemes of whatever length it feels like 

The first approach is called Connectionist Temporal Classification (CTC), and the second approach is generically referred to as an end-to-end sequence-to-sequence model (sometimes called Seq2Seq models in early literature).

### CTC 
CTC is a general method for identifying a sequence of symbols from an underlying complex signal that corresponds to those symbols. Roughly speaking, CTC works as follows:
- You define an "alphabet" of symbols that your model is able to produce (for ASR, the alphabet is generally "the set of all phonemes used in the languages supported by the model" plus a special "blank" symbol.)
- You define a "window size" for your input data which is the minimum width in your input that might correspond to a single symbol of your output sequence (for ASR, this might be something like "10 ms", meaning you expect every phoneme in the input speech to be at least 40 ms long)
- You "slide" the window from left to right over your input signal and at each step you produce a probability estimate for each symbol in your alphabet.  The output of each step is an array the same size as your alphabet that sums to exactly 1. Once you've slid over the entire input signal, you have an array of size M x N, where N is the number of symbols in your alphabet and M is the width of the input signal divided by the window size [Aside] In practice you might choose a window stride that is different than your window size, but for the sake of simplicity here we assume they are the same [/Aside].  This array is typically called the "lattice" in CTC.
- You define a "language model" that specifies a cost for transitioning between two symbols.  Historically this was often an "n-gram" language model, meaning you'd specify sequences of length n that are more or less likely to show up in your output sequence. [Aside] these n-gram models were typically learned automatically from some large corpus of real data rather than hand-coded. [/Aside] This allows you to bias the model toward producing "real" words, while still allowing it to output symbol combinations that aren't found in the language model.
- Finally, you "decode" the output sequence by finding the "minimum cost path" through the lattice. The "minimum cost" is calculated with a dynamic programming algorithm (Viterbi decoding) that incorporates both the likelihood of the individual symbols calculated for each window step and the likelihood of the various n-gram sequences in the language model [Aside] repeated symbols are typically "merged" together into a single instance as part of the decode step (because a single phoneme duration might extend beyond the window size) [/Aside]

Notice that CTC only works if the underlying input signal has a dimension that is monotonically aligned with the output synbol sequence, meaning that sections of the input sequence that corresponds to output sequence symbols aren't in "different order" than the output sequence symbols themselves.  For example, "time" is the monotonically aligned dimension for audio data; if phoneme A shows up before phoneme B in the audio, then the symbol(s) corresponding to A are guaranteed to show up before the symbols corresponding to B in the transcript. [Aside] Most (but not all) writing systems also have this property - for example, in Latin script "left to right" is the sequence direction for characters when rendered on a page, and ALSO the sequence direction for the unicode codepoints that correspond to those characters.  For this reason, SOTA OCR models circa 2020 were also using a CTC approach.[/Aside]  However, any pair of two different languages are generally not monotonically aligned (some put the verb at the beginning, some at the end, etc), making CTC a bad fit for cross-lingual tasks such as translation.

After CTC you end up with a sequence of phonemes, which can then be converted into a transcript through a lexicon that maps phonetic components onto words (and allows for things like disambiguating homophones based on surrounding context).  A key thing to notice about CTC is that the acoustic model, language model, and lexicon are all completely independent (i.e. they are trained and optimized separately) [Aside] Note that it is in principle possible to incorporate "language model-like" information in the acoustic model if you pick an architecture for your acoustic model that incorporates sequence information (for example, an RNN, or an attention-based model).  You can even use a transformer backbone for your acoustic model and still do CTC-style Veterbi decoding if you want (this exact approach was used in Google's USM model in 2023 with a conformer-based encoder - https://arxiv.org/pdf/2303.01037)) [/Aside]

### End-to-End Sequence-to-Sequence models

The primary challenge the CTC architecture is trying to solve is finding an alignment between the input and output sequence (i.e. which parts of the audio correspond to which output sequence symbols).  This is hard for lots of reasons, one important one being that you generally don't have very much training data where the alignment is accurately annotated; this also means that if you can find a training method that can leverage unaligned data, you have way more data to train on.  Thus, an alternative to an explicit alignment technique like lattice decoding is to train an end-to-end sequence-to-sequence model.  This pushes the complexity of learning an alignment into the model itself, so it generally takes a lot of training data and a fairly large model (compared to classical architectures, not compared to modern LLMs).  

The classic architecture for this sort of problem is a Recurrent Neural Network, an over the 2010's several alternative architectures emerged to improve upon standard RNNs, including RNN-Transducers (https://arxiv.org/abs/1211.3711), attention-based methods (https://research.google/blog/improving-end-to-end-models-for-speech-recognition/), and Conformers (https://arxiv.org/abs/2005.08100).  

One major downside of these approaches is they all operate in "batch mode" - you have to give the model the entirety of the audio you want to transcribe before it can start working, which means that if you want to support "streaming" you have to implmenent some external "chunking" algorithm to break up the input audio, which introduces both complexity and additional sources of error.  An important innovation that happened in the early 2020's was extending the RNN-T architecture to operate in a natively streaming way (https://research.google/blog/an-all-neural-on-device-speech-recognizer/)

We're obviously eliding over lots of complexity here, but the big takeaway is that over time we moved from a cascade of modular independent components into big end-to-end models that scaled well by pre-training on unabled training data, a harbinger of things to come.

## Acoustic Models as Audio Tokenizers

The "acoustic model" component of an ASR model (whether trained independently or as an integrated component of a single end-to-end model) is conceptually responsible for something like "building a good context-dependent representation for what phoneme is being verbalized at any given point in time."  Notice that if you consider "speech" to be something analogous to "language encoded in the audio domain," then if you squint real hard at the internal state of the ASR acoustic model it might start to look simillar to the language model embedding of a text token - i.e. a function that maps an individual input token (e.g. a subword or a spectrogram frame) into an embedding space that some downstream model (e.g. a transformer) can process effectively (e.g. with cross-attention).

This is in fact exactly what early versions of audio-enabled LLMs did; they used a quantized internal state of an ASR model as the "audio tokenizer", and then trained an LLM on a token vocabulary that included both audio tokens and text tokens. This turned out to have a few issues, which we'll cover in the Tokenizer section below.

### TTS Circa 2020

Text to Speech is the task of producing natural, high-quality speech from a transcript.  Here again there are several subtly different formulations of the problem with different requirements; depending on the context, you may want:
- pronunciation control
- speaker control / multispeaker models
- accent control
- speed / timing control
- style / emotion / affect control
- deterministic output
- vocal burst support
- trading off naturalness / expressiveness vs. word error rates
- multilingual models

There are basically 3 big challenges in TTS:
1) Control / accuracy - does the model output speech that accurately corresponds to the correct pronunciation of the words in the transcript?
2) Acoustic quality - does the model output speech that sounds like a real person's voice, or speech that sounds like a robot?
3) Naturalness & Expressivity - there are many valid prosodic interpretations of a given transcript; does the model output speech that is appropriately natural and expressive for the transcript in the broader context of where the model is being used? (e.g. stylistically appropriate to the setting, consistent with past and future utterances from the same transcript block / agent, affectively consistent with the semantic content of the utterance, etc.)

Classical models mostly had #1 and #2 solved in the late 20-teens, but #3 remained a stubbornly open challenge until the latest wave of Transformer-based models.

### How TTS Models Work(ed)

Frontend, acoustic model, vocoder


### TTS metrics
Word Error Rate / Phoneme Error Rate
MOS
MOS SxS
Volume confounding
MOS is wildl unreliable

Tacotron
Griffin-Lim
Convolutional Neural Networks
Hidden Markov Models


### Launching Transformer-based Models

You may notice that #1 is in direct tension with #3.  The common wisdom a few years ago was that TTS users REALLY cared about accuracy, and early progress on transformer-based TTS models (which were significantly more natural and expressive, but suffered from higher rates of hallucination and catastrophic failure) was slow to launch because entrenched TTS providers didn't see the user value.  It wasn't until ElevenLabs came along and definitively demonstrated the pend up user demand around more natrual and expressive models that established players started shifting their thinking. [Aside] To be clear, ElevenLabs definitely has SOTA speech generation models. But they also benefited from a 6-12 month head start due to the shortsightedness of encumbents that had nothing to do with technical progress. [/Aside]

Option 1: control knobs
Option 2: 
Long-run context is important
Context prompting
