# AudioAIExplainer
Writing down everything I (think I) know about audio AI systems

## What Is Audio?

### Pressure Waves
What humans perceive as "sounds" are actually pressure changes in the air over time.  

A local pocket of high air pressure (aka compression) is created when something physically pushes air molecules together. Those air molecules have to come from somewhere, so this also creates local pockets of low pressure somewhere nearby. Air molecules in the high pressure area push outward into any low pressure areas around them, while air molecules around any low pressure area push inward to fill the vaccuum.  As the nearby air moves around to equalize these pressure differentials, it creates new pressure differentials with the air on the opposite side of the original disturbance, which in turn try to equalize, create new differentials, etc.  This ultimately creates pockets of high and low pressure that propogate outward from the original point in a shape that we call "waves" (these are exactly the same fluid dynamics that cause ripples when you drop a pebble in water). When you "hear" a sound, that is your brain interpreting these pressure waves. [Aside] See https://nsinstruments.com/principles/approaches.html for a deeper explanation [/Aside]

[GIF] visualization of a sin wave oscilating, and below that an aligned visualization of scattered particles on a 2D plane moving in such a way as to show the "wave" passing through them [/GIF]

Waves have both a *frequency* (how "quickly" the wave oscillates, aka the inverse of the "period") and an *amplitude* (how "high" the wave goes from top to bottom). 

[Image] a sign wave with the amplitude and period visually identified showing the equation "frequency = 1 / period" [/Image]

Because audio is a *time varying* signal (i.e. the x-axis is time), the period is measured in seconds and the frequency is measured in Hertz (number of cycles per second). The typical range of human hearing is roughly 20 Hz - 20 kHz (which tends to decrease to around 8-12 kHz in our 50's and 60's).

The amplitude of a sound wave corresponds to "volume" or "intensity" of the sound, and the y-axis is literally a measuring the air pressure at a given point in space over a period of time (the x-axis). If you remember your chemistry, the ideal gas law states that PV = nRT, or pressure = number of particles x constant x temperature / volume.  Temperature is defined as the average kinetic energy (kg x m^2 / s^2) per particle of a gas, so the units of pressure are generally given as "Newtons per square meter" (aka "Pascals"), where a Newton is a unit of force (measured in kg x m / s^2).  "Force per square meter" is conceptually useful, as you can think of pressure as "the amount of force exerted by a volume of gas on a container trying to hold that volume of gas", which aligns with most people's understanding of pressure.

While pressure can be measured "objectively" as Newtons per square meter, it turns out this is not how we actually talk about sound volume.  Instead, we talk about sound volume in units of decibes (dB), which is a *relative* unit of measure expressing the ratio of two values of a power or root-power quantity on a logarithmic scale (in this case sound pressure is a root-power quantity, meaning the square of sound pressure is proportional to power).  What this means in practice is that if you have two time-varying pressure signals (e.g. two sound waves) X and Y, you can calculate the root mean square of the each (i.e. the average value of the square of the pressure measurements of each signal over a given time period), and the dB value relating the two is proportional to the log_10 of the ratio of the RMS values (specifically, X would be considered 20 * log_10(RMS(X)/RMS(Y)) dB louder than Y).  

That's a lot of big words to make the simple point that *dB is a relative unit of measure*.  When people talk about a sound being "90 dB", what they mean is "90 dB louder than a particular reference sound."  In audio, the reference sound is basically always 20 micropascals (μPa), which is generally considered "the quietest sound a human can hear" and would correspond with a volume of "0 dB" in common usage.

[Aside] Because dB is a generic measure of the ratio of two signals, it can occasionally be an overloaded term in the audio space; for example, the primary metric used in audio separation and enhancement tasks is Signal To Noise Ratio (SNR), which is also measured in dB (or dB gain) with the ground truth "noise" as the reference signal (as opposed to the 20 μPa reference sound used for sound volume). [/Aside]

Note that the amplitude of an air pressure wave changes over both time and distance; the farther you get from the source of the wave the smaller the amplitude gets (due to the inverse square law), and for a given distance away from a sound source the amplitude will decrease over time (due to energy loss through friction and absorbtion).  For simplicity, some audio analysis techniques assume that audio sources and receivers remain fixed in space, and conduct analysis on a small enough time scale that amplitude decay is negligible.  But in the real world sound wave propogation is a complex and dynamic system.

[Aside]If you are anything like me, you may be bothered by the fact that (all else equal) pressure changes with the temperature of the medium, so you can't actually talk about "sound pressure" without talking about the air temperature at the time the signal is propogated.  I have no idea how ambient temperature affects human perception or microphone recording of audio, nor do I know if any issues arise when comparing signals captured in different ambient temperatures; however, my rough understanding is that "it's a small enough deal that it doesn't matter in practice" [/Aside]

sources: https://en.wikipedia.org/wiki/Sound_pressure#Sound_pressure_level, https://en.wikipedia.org/wiki/Decibel, https://nsinstruments.com/principles/approaches.html


### How do waves combine together to create sound?
Here's an example of what a single 12 KhZ wave sounds like:

[Audio] audio of a single sin wave at 12 KhZ[/Audio]
[Image] image of a single sin wave [/Image]

Of course in the real world audio is not just one wave at a time, it's many overlapping waves happening at the same time. When two waves are propogating through the same medium at the same time, the amplitudes add together and the resulting signal (called the "interference") is a "complex tone" made up of more than one frequency. Here's an example of two different frequency waves played at the same time:

[Audio] audio of a sin wave at 12 KhZ plus a sin wave at 7 KhZ[/Audio]
[Image] image of a the combination of a 12 KhZ signals + a 7 KhZ signal [/Image]

The human ear is very good at interpreting an interference pattern and understanding which frequencies are present.  There's a surprising amount about the ear that we still don't understand, but roughly speaking we have thousands of hair-like cells that each oscillate with different frequency ranges (Source: https://nsinstruments.com/principles/approaches.html).  We'll talk below about the Fourier Transform, which is a mathematical technique that lets us identify the individual frequencies present in a complex tone.

Humans interpret some combinations of frequencies as "sounding better" together than others. While some aesthetic judgement is certainly cultural and individual preference, much of it is deeply rooted in the mathematical relationship between the frequencies.  For example, an "octave" in music is an interval between two notes where the higher note has double the frequency of the lower note, and the C major chord has a frequency ratio of 4:5:6.  

[Audio] audio of 3 sin waves playing a c major chord [/Audio]
[Image] image of the above sin waves together [/Image]

### Phase
Human ears can identify (and often have preferences for) frequencies that are integer multiples, share common divisors, or are otherwise mathematically related to each other.  However, if you naively play these frequencies together, it can sound wrong in a way that is *extremely noticeable* to human ears:

[Audio] audio of a sin wave at 12 KhZ plus a sin wave at 9 KhZ[/Audio]
[Image] image of a the combination of a 12 KhZ signals + a 9 KhZ signal [/Image]

[Audio] audio of a sin wave at 12 KhZ plus a sin wave at 8 KhZ[/Audio]
[Image] image of a the combination of a 12 KhZ signals + a 8 KhZ signal [/Image]

What's happening here is that precisely because of the mathematical relationships of the waves, the peaks are lining up with each other in some regular periodic way, creating a "strobing" effect in the interference pattern where the pressure amplitude of the sound wave is much higher where the waves intersect than where one peaks without the other. 

However, consider what might happen if one of these waves was "shifted over" by a bit in time.  You'd still be hearing the same two frequencies, but the peaks would no longer line up, which would remove the unpleasant artifact you hear in the original.

[Audio] audio of a sin wave at 12 KhZ plus that same frequency phase shifted 48 degrees[/Audio]
[Image] image of the above waves in isolation and the interference pattern from combining them [/Image]

We call the amount of "shift" in a wave the *phase*.  Specifically, because we model all waves as sign waves, and each point in a sin wave cycle corresponds to an angle of a circle, phase is measured in degrees.  The phase difference between two waves can be defined as a difference in their initial angles around the circle. A difference of 180° means the waves are completely out of phase, or inverted relative to one another.  

[Aside] Much like dB, phase is not a fact about an individual wave in isolation, but rather about the relationship between two different waves (or an individual wave relative to a particular point in time).  If you compare two waves of different frequencies, the phase difference between them will be constantly changing over time.  The phase difference itself will be periodic, and for signals that are small integer ratios of each other, the phase difference might be periodic with a frequency above 20 Hz, which is within the range of human hearing! This is that low buzzing you're hearing when you listen to overlapping tones with e.g. 30 Hz phase shift [Audio] Audio of two tones with a periodic phase shift of 30 Hz [/Audio] [/Aside]

Shifting the phase of interfering waves can have a dramatic impact on the phase and amplitude of the resulting sound, which in turn can dramatically impact human perception. If you play the exact same sound at a 180 degree phase shift with itself, the interference will cancel out the original sound and anyone listening would hear silence (this is how sound cancelling headphones work).  If you play the exact same sound to each ear, but one of them slightly phase shifted, the human brain will perceive a "binaural beat" [TODO: link] auditory illusion. If you play all frequencies at the same time with the same amplitude (aka white noise), shifting the phase over time can lead to different "texture" of the sound.

[Aside] When you combine two sin waves of the same frequency but different phase and amplitude, the resulting signal will be a sin wave with the exact same frequency, but a different phase and amplitude (both of which depend on the relative phase of the waves you combined).  This is (apparently) the basis for a huge number of audio effects, like phasers and filtering.  See https://nsinstruments.com/principles/linear.html [/Aside]


[Audio] audio of a complex combination of sin waves at differnet frequencies, amplitudes, and phase shifts [/Audio]
[Image] image of the above waves in isolation and the interference pattern from combining them [/Image]

[Audio] audio of the same frequency waves as above, but at differnet amplitudes and phase shifts [/Audio]
[Image] image of the above waves in isolation and the interference pattern from combining them [/Image]

That's it.  That's all sound is. **All sound is fully specified by the frequency, amplitude, and phase of the pressure waves propogating through a given point in space over time.**  I know these toy examples don't sound like "real audio" - we'll talk about that more below - but it's important to understand that "sound" is just your brain interpretting extremely complex and time-varying combinations of the above.

[Aside] If you combine multiple independent audio sources playing the same "note" (e.g. a chorus of singers, or multiple instruments playing the same part in an orchestra) statistics can give you a rule of thumb for the average expected increase in amplitude based on phased interference; this is why two people singing together isn't twice as loud as a single person.  However, if you instead have multiple microphones recording the same audio source and mix them together, the phases of the various partials are no longer independent and can result in dramatically different changes in volume. See https://nsinstruments.com/principles/linear.html for a good explanation. [/Aside]

Sources: https://nsinstruments.com/principles/linear.html

### Fundamental Frequency and Timbre

In the real world, you're usually hearing thousands of overlapping frequency waves with different levels of energy that your brain is automatically synthesizing into the experience of "hearing."  The human brain tends to group certain combinations of frequencies together as a single "sound" even though they are actually made up of complex combinations of frequencies.  The specific combination of frequencies is called the "timbre" of a sound, and this is why two different instruments playing the "same frequency" of note sound different to human ears.  

When people talk about the "frequency" of a note played by an instrument (or sung by a human), they're talking about the "fundamental frequency" (often referred to as f0) which is the lowest (and often perceived as the "loudest") frequency present in that complex tone.

### Frequency Bands
Frequency is an analog value, meaning it is continuous and can be specified to essentially arbitrary precision.  However, in the real world there's a limit to the precision with which we can measure and produce specific frequencies, and the frequency of a signal can shift over time.  Given that nearby frequencies tend to behave similarly, it is often useful to think in terms of frequency ranges, which we generically refer to as "frequency bands" (e.g. "5 kHz - 6 kHz"). 

There is no single correct way to bucket frequency ranges together, but there are conventions depending on the context. Frequency tends to behaves in logarithmic ways (i.e. the ratio of two frequencies is generally more important than the absolute difference between them), so frequency band conventions are often simillarly logarithmic (e.g. 50 Hz - 100 Hz might be one band, while 4 kHz - 8 kHz might be another band).

### Reflection
When sound propogates through an environment, the air pressure waves impact and bounce off of solid objects in the environment (walls, trees, the ground, other people, etc). The amount, direction, and diffuse / specular nature of reflection depends on the characteristics of the surface impacted - the smoothness / roughness, the elasticity of the material, the geometry of the object, etc. These characteristics are frequency dependent, meaning sound waves will reflect off of materials differently depending on the frequency. These reflections dramatically impact the character and quality of a sound, and are what makes the same audio sound different depending on the enviornment you're listening in.

[Aside] At high amplitudes, a material's reflection can become amplitude dependent as well when the sound wave starts affecting the properties of the reflecting material itself. [/Aside]

[Image] A top-down view of a square room with an audio source with arrows showing how audio might reflect off nearby walls in a specular way.  Image is labeled as "low frequency spectral reflection" [/Image]

[Image] A top-down view of the same square room as above with an audio source with arrows showing how audio might reflect off nearby walls in a diffuse way.  Image is labeled as "high frequency diffuse reflection" [/Image]

### Reverberation & Room Impulse Response

A listener in an enclosed room will hear not just the original sound, but also the reflections (and reflections of reflections, etc) off of surfaces in the room. This leads to the same signal arriving at a given point in space at a very slight delay and from different directions and with diminishing amplitudes.  The repetition of the same signal at a very slight delay is referred to as "reverberation," and reverberation caused by the reflections of sound off of walls is called the "room impulse response."  Note that the room impulse response depends on the location of both the audio source and the listener; different positional combination in the same room will have a different room impulse response.

[Aside] The distinction between reverberation and echo is largely arbitrary; reverberation is conventionally defined as "repeating signal at < 50 - 100ms delay" while echo is defined as "repeated signal at > 50 - 100ms delay." However, the human brain tends to interpret echo as "repetition of the original sound" and reverb as "part of the original sound" [/Aside]

Reverberation is itself often frequency dependent, and you can characterize reverb as "for a given initial impulse signal, how much of the energy present in each frequency band of the original signal will be repeated back at what time delay?"  

In principle you could try to describe some function estimating the amount of energy from the original signal that will arrive at the source for each frequency band over time. In practice, reverb is sometimes characterized by a single number describing how long it takes for a 60 dB reduction in energy in a given frequency band (or sometimes just a single number for the whole 20 Hz -20 kHz band). In cases where more precision is needed, we typically bucket time blocks together much like we bucket frequency bands together and record energy decay for each time bucket x frequency band combination.  For example, we might say "for the 50 Hz - 100 Hz frequency band, room reflections will result in 80% of the energy in the initial signal being present for the first 10ms, 70% for the next 10ms, 65% for the next 10ms, etc."  By convention, these time buckets are generally linear rather than logarithmic, and are typically specified as 10ms chunks.

Note the structure of this 2-dimensional characterization of reverberation - there is a different "percentage of energy" value for each frequency band for each time period.  To visualize this data you can create an image where the y axis is frequency band, the x-axis is time, and the color of each pixel (or box) corresponds with the energy level.  This concept of visualizing quantized 2 dimensional time x frequency data as an image is important, and will come up again when we describe how audio is digitally represented as spectrograms.

[Aside] In fact, the "energy per frequency band over time" that you would use to describe a room impulse response is literally the same thing as a spectrogram, so there's nothing stopping you from treaing an RIM as audio and "playing" it out loud. The results sound kind of cool, and will give you a good idea of how the RIM will affect any audio it's applied against [Audio] example audio of a room impulse response [/Audio] [/Aside]

Reverb and room impulse responses can be estimated from microphone recordings of real audio samples, or they can be simulated in software [Aside] This is essentially the same thing as a 3D graphics rendering engine.  You set up some 3D model and specify the characteristic behavior of all of the surfaces, then you "raycast" audio out from a point source and calculate what shows up at the targt recording point. [/Aside]. Once a reverberation profile has been obtained, it can be applied to an audio signal as a processing technique (often used to add reverb to a digital signal often makes it feel more "real"), which we'll talk about in more detail when we get to the spectrogram discussion below 

[Audio] example audio of TTS or music output without reverb and with reverb to show the difference[/Audio]

### Head related transfer function

Reverberation doesn't just come from reflection off of surfaces.  It also comes from individual components, materials, or objects that are part of or in contact with the audio source (e.g. the neck of a guitar, or the body of a piano, or the through muscles of a singer, etc).  Simillarly, reverberation happens when elements connected to the listner (the housing of the microphone, the tissue and bones of an individual's facial structure, etc.) In particular, every human has their own unique "head related transfer function" that describes how a signal will propogate through their own particular anatomy.  My understanding is its a little unclear how unique the HRTF actually is (and how important a custom HRTF is for a good listening experience for extreme audiophiles), but nonetheless its important to note that your own body affects the characteristics of the sound you actually experience.

[Aside] This is why your voice sound different to you than it does on a recording - when you speak, your vocal chords are vibrating to produce waves in the air in your vocal tract that everyone else hears (and get recorded by any relevant equipment).  However, they're also producing resonant vibration and reverberation in your own skeletal and muscular structure, which your ears are picking up in addition to the frequencies propogating over the air.  You are literally hearing something different than everyone else when you speak [/Aside]
https://en.wikipedia.org/wiki/Head-related_transfer_function


### Localization, Multichannel & Spatial Audio

The reason most animals have two ears rather than one is that it allows for sound source localization.  Because the ears are placed some set distance apart, the brain can use the differences between the signals received by each ear to infer which direction a sound is coming from (simillar to depth perception in the visual domain).

[Aside] While time delay is the primary signal used for spatial localization of audio, there are actually too many degrees of freedom to accurately do 3-dimensional localization with only 2 signal receivers; a sound from directly above you would have the same relative delay to both your ears as a sound directly below you.  Your brain uses other signals (such as the head related transfer function discussed below) to disambiguate directionality in 3 dimensions. [/Aside]

Because of this, digital media replayed from a single speaker tends to lack a depth quality present in real audio, particularly in video where the user "expects" audio from different sources on screen to come from different directions. To improve the user experience, digital recordings might have more than one "channel" of audio. Typical audio formats include "mono" (one channel), "stereo" (two channels, one left and one right), and "spatial" (a variety of public and proprietary formats).  Most playback devices (laptops, tablets, headphones, etc.) have at least a left and right speaker to support stereo output. Spatial audio formats allow for speakers placed in different locations to allow audio to "sound like" it's coming from a particular place, which can significantly enhance the listening experience for some content, but is generally not well supported in most consumer content ecosystems today (mostly home theaters and movie theaters).  

[Aside] There has been work over the last few years to move toward broader adoption of spatial audio playback for consumer headphones.  This requires both the broad adoption of spatial audio formats on the recording side (or ML models to "upsample" mono/stereo content to spatial), as well as technological progress on the playback side (primarily head tracking and cheap and easy measurement of individual head related transfer function & individual room impulse response) to allow the headphones to dynamically alter the audio playback for each earbud. Both Android and iOS have some level of spatial audio support, but it needs to be manually enabled, and the content availability is still not super broad.  I have no idea how good the spatial audio is when enabled on either platform. [/Aside]

[Aside] If you've heard of "5.1 surround sound", that's a Dolby proprietary standard that has 5 predefined directional channels for a known physical configuration of 5 speakers (front left, front right, front center, back left, back right) and one subwoofer channel (specifically for low frequency sounds).  Simillarly, "7.1 surround sound" has 7 predeifined directional channels and one subwoofer.  Dolby Atmos is the name of their proprietary spatial audio format that allows for arbitrary placement of audio sources in 3D space; Atmos format audio can then be "rendered" to a specific set of speakers with a given spatial layout (which could be 5.1 or 7.1, or could be your own custom speaker setup). [/Aside]

Recording stereo audio requires multiple microphones with a known spatial relationship (aka a "microphone array"), and most consumer recording devices (e.g. phones) come with a mic array of between 2-8 mics.  [TODO: verify this is correct] For simplicity, we will mostly talk about mono channel audio going forward, but in principle most approaches, techniques, and concerns generalize to multichannel audio.

## How is audio digitally represented?

Audio is a continuous analog signal, which cannot be represented directly in a computer.  Instead, computers operate on digital approximations of those signals - for example, images are typically represented as arrays of pixels with discrete rgb values between 0 and 255.  Simillarly, audio is represented a sequence of amplitude values ("samples") that correspond to the value of the sound pressure wave at a given point in time (the "audio waveform").  These samples always occur at a constant rate (called the "sample rate") within a given audio file, meaning the time interval between any two consecutive samples is the same.  The sample rate is measured in Hertz (samples per second).  For example, if you have a sample rate of 200 Hz, that would mean you store 200 pressure values per second. When audio is analyzed or played back on a speaker, you can generally think of it as interpolating between these discrete points - for example, a speaker that needs to output pressure A at t = 0 and pressure B at t = 1 will try to linearly transition from A to B over that timespan. 

The most common audio files are .wav and .mp3.  While technically wav files support mp3 encoding, generally speaking wav files store the raw audio waveform values in an uncompressed way, and mp3 files store audio that has been compressed in a lossy way.  Regardless, both ultimately produce a sequence of sample points at a given sample rate that are sent to the audio output device at playback time. [Aside] Mp3 is a highly optimized standard with lots of moving parts, but roughly speaking the mp3 compression algorithm mirrors the process of spectrogram generation via Fast Fourier Transforms discussed below. Once a frequency domain representation is produced, further processing removes frequency components that are considered by psychouacoustic analysis to be perceptually unimportant or unhearable - for example, louder noises tend to mask quieter noises at neardy frequencies. The audio is stored as this reduced frequency domain represntation, and synthesized back into audio waveform samples by a decoder at playback time. [/Aside]

Video files typically store audio data in an independent datastream from the video frame data.  The audio datastream could be encoded in a myriad of ways depending on the video format, but you can roughly think of a video file as "a sequence of images and an audio file that have been glued together."

### Sample Rate & The Nyquist Frequency

Common sample rates for digital audio are 8 kHz, 16 kHz, 24 kHz, and 48 kHz (often referred to as 8k, 16k, 24k, and 48k).  

[Aside] If you Google it today, you'll see lots of sources saying that most audio is 48k, but my experience has been that a shockingly large amount of audio data used in research is 16k or 24k.  My guess is that a substantial amount of audio data captured and uploaded to the internet in the early 2000's and 2010's was at lower sample rates, but as consumer devices have improved, so has typical recording quality. As of January 2025 when I left Google, to my knowledge none of our models were being trained on any high-scale 48k audio datasets (though efforts were underway to migrate in this direction) [/Aside]

Some audio is recorded or produced in 96k or 192k, but the difference between these and 48 kHz is unlikely to be perceptually distinguishable by humans.  The reason for this is because of something called the Nyquist-Shannon Sampling Theorem, which says that if a signal is sampled at a rate at least twice its highest frequency component present in that signal, the original signal can theoretically be perfectly reconstructed from the samples.  We will discuss this in more detail in the Fourier Transform section below, but in practice this means that 48k audio data is capable of encoding any signal up to 24 kHz frequency (the maximum encodable frequency is called the "Nyquist frequency," and is always half the sample rate frequency). But as we said before, typical human hearing range is roughly 20 Hz - 20 kHz, deteriorating to 8 kHz - 12 kHz as we age into our 40s and 50s, so any signal that can be heard by most humans can be encoded in 48k audio.  

[Aside] Nevertheless, you will find audiophiles who claim to hear a difference between 48k and 96k audio.  It's possible that lower sample rates may create artifacts because of hardware limitations, processing artifacts, or other things beyond the theoretical limitations of the Nyquist frequency, but we can at least conclusively say any such differences are negligible except in the most extreme of listening and recording environments. [/Aside]

Note that the fundamental frequency of human speech generally ranges from ~80-300 Hz, with most of the speech energy concentrated from 250 Hz - 5 kHz.  Most 8k audio data used in audio research comes from the US telephony stack, which uses an 8k sample rate (and therefore can capture signals at 4 kHz and below).  This is why telephone calls sound "compressed" - they are missing the high frequency bands typically present in human speech.  This is also why historical text-to-speech models have been limted to lower sample rate output (often 16k or 22k).  However, some specific elements of speech occur above the Nyquist frequencies for these sample rates (for example "sibilance" is the sharp hissing audible in "s" and "sh" sounds, and mostly occurs from 5 kHz - 10 kHz, but may go even higher). Newer TTS models are trained on and produce higher sample rate audio, and arguably this is a contributing factor in the improved perceptual quality of recent models (particularly as they become more prosodically expressive as they adopt Transformer architecture backbones as discussed below)

A funny complicating factor here is that many senior audio researchers are in their 40s and 50s and have likely lost some sensitivity to higher frequency band; so the people leading research may not be able to tell a difference between 24k and 48k audio even if you can!

### Bit depth

In addition to sample rate, the bit depth is the second important dimension of an audio waveform encoding.  Bit depth is just "how many bits are used to represent the value of an individual sample?"  Typical values for bit depth are 16-bit and 24-bit, and historically these are measured and stored as signed integers. [Aside] I do not have a good understanding of how these 16- or 24-bit values are actually utilized in practice.  One might expect that pressure levels would be normalized to some "maximum allowable amplitude" in the given encoding scheme and then each bit step increase would represent a 1 / maximum amplitude increase; this would avoid constantly wasting bits as 0's that never get used. However in practice it seems like different encoding schemes treat this differently, up to and including just using a standard floating point number and clamping all values from [-1.0, 1.0].  In the end this isn't a very important detail for our purposes, but I feel compelled to admit that I don't understand how this works well enough to implement it today. [/Aside]

You may hear audio quality described in terms of "bitrate."  The bitrate is literally just the bit depth x sample rate.  So a 48k sample rate at 24 bits would be 1,152 kbps (1.15 mbps)

### Microphone limitations
Saturation

### Speaker limitations
Frequency response

### Frequency Decomposition & Fourier Transforms

As we discussed above, complex tones are made up of a combination of simple component frequencies. The amplitude of these component frequencies (possibly shifted by some phase) are added together to produce a single interference pattern, which is the actual pressure wave that propogates through the air and produces sound.  When you "hear" that sound, your ears and brain are decomposing the interference pattern into its constituent frequencies; you can "tell" that a given interference pattern consists of a 400 Hz, 500 Hz, and 600 Hz signal. Humans do this by having physical elements in the ear drum that resonate with different frequency ranges; you literally have nerve cells in your ear that are responsible for detecting the amplitude of any frequency between 50-55 Hz [TODO: find numbers of a real cel group] present in a given sound.  The brain then interprets these signals over time to form your sense of hearing. 

Not only is this how human anatomy appears to process sound, but the Fourier Series Theorem says that, for a reasonable set of constraints, any continuous periodic function can be represented as a sum of sines and cosines with different frequencies and amplitudes. In other words, a complex periodic signal can be decomposed into its constituent sinusoidal components, and if you have the amplitude and phase values for each of the constituent sinusoidal components, you can perfectly reconstruct the original signal.  So characterizing a waveform as "the amplitudes and corresponding frequencies for the set of sin waves necessary to reconstruct that waveform" is both a) always possible, and b) does not lose any information.

In mathematical terms we refer to this this as transforming a time-domain signal (with amplitude as the y axis and time as the x axis) to a frequency-domain signal (with amplitude as the y axis and frequency as the x axis).  That output of this transform would show you for a given signal, what are the underlying frequencies present that make up that signal?

[Image] Image showing time and frequency domain side by side[/Image]

We call this transform the Fourier Transform, and it is formulated as follows:

[TODO: add fourier transform math]

Likewise, we have the Inverse Fourier Transform, which takes a series of complex number coefficients representing the amplitude and phase of individual sine waves and converts it back into a time domain audio waveform:

[TODO: add inverse fourier transform math]

We are not going to go through all the math behind the Fourier Transform here, partly because I don't have the requisite expertise, and partly because there are plenty of good explanations out there already (this video is great: https://www.youtube.com/watch?v=spUNpyF58BY).  However, in the name of completeness I am going to at least trace a few of the underlying intuitions.  If you don't care, feel free to skip to the next section and just take my word for it that we have a reliable way to decomponse a complex wave into the underlying frequency components.

### Intuitive Explanation of the Fourier Transform

Imagine we had a magical oracle where we could plug in an arbitrarily complicated periodic function s [Aside] Meaning s can be perfectly reproduced by combinging some finite number of component sine waves with different frequency, amplitude, and phase values [Aside] and a frequency value f, and *if and only if f is a component frequency of s*, our oracle would output a value representing the amplitude of that component frequency in s. In all other cases the oracle would output 0.  If we had such an oracle, then we could simply graph the output from f = 0 to f = 20,000 Hz for our given signal, and we would see spikes at exactly the component frequencies present, where the size of the spike tells us the amplitude of the component sine wave.

Now how would we build such an oracle?  Let's imagine you wanted to check whether a target frequency f was present in the signal. The first thing you could do is take the complicated periodic input function s and chop it up into blocks exactly the size of the period of f.  So if the f you're investigating is 4 Hz, then you chop up s into a bunch of blocks each 0.25 seconds long.  Next, imagine you stacked a bunch of those chopped up sections on top of each other and averaged them all together. 

[Gif] gif showing the above in an animated way [/Gif]  

Note that if there is some periodic signal at exactly f = 4 Hz, that signal would be *exactly the same in every single one of those blocks*, so the interference between that signal and itself would be *constructive* as you added more blocks; it wouldn't get "averaged away" as you added more blocks on top of each other.

Now consider all the frequencies *other* than this target frequency. Observe that these frequencies fall into two categories: 
1) For the frequencies that are some integer n multiple of f, they will undergo exactly n cycles within the block window.  For example, f = 8 Hz will undergo exactly 2 cycles in a 0.25 s window, f = 12 Hz will undergo exactly 3 cycles, etc.
2) Any other frequency will undergo a fractional number (i.e. not an integer number) of cycles within the window.  The number of cycles is given by the ratio of the frequency to the target frequency.  So for example, a 6 Hz signal will go through 6 / 4 = 1.5 cycles per 0.25s window, and a 9 Hz signal will go through 9 / 4 = 2.25 cycles per 0.25s window.

We'll deal with case #1 in a bit, but for now let's focus on case #2.  If a wave undergoes a fractional cycle, that implies that the wave will be in a different phase at the start of the next window.  Whatever this phase change is, the same amount of phase change will happen between the second and third window, and the same phase change will happen again between the fourth and fifth window, etc.

[GIF] GIF showing the above [/GIF]

If the ratio of the target frequency and the frequency we're investiaging is a rational number (i.e. can be represented with a whole number fraction), then eventually this phase will come back around to zero (possibly taking several "loops" between 0 and 2 pi at different values - but always the same interval - before landing exactly on 2 pi).  If you took all the phase value this wave had at the start of each block in the sequence before it comes back around to zero and you sorted them from lowest to highest, you would find these phase values are always *uniformly distributed* between 0 and 2pi (meaning the distance between neighboring points is equal to 2pi / N, where N is the number of blocks taken to cycle the phase back to 0). 

[Aside] IF the ratio of the target frequency to the frequency we're investigating is an irrational number, then the phase will never come back around to zero - but the phase values will be uniformly distributed over [0, 2pi| so the logic we use below still holds [/Aside

For example:
Let:
𝑓_𝐵 = 1 Hz (base wave)
𝑓_𝐴 = 1.3 =1.3 Hz (slightly higher frequency)

After each cycle of 𝑓_𝐵, we track the relative phase of wave A. Each cycle of B is exactly 1 second, so we check wave A every 1 second. At time t = n, the phase of wave A is:

ϕ_n = 2πf_A x n mod 2π = 2π⋅x 1.3⋅x n mod 2π

or

θ_n = 1.3 n mod 1

This is a fractional rotation on the unit circle by 0.3 per step

Let’s compute a full cycle:

n	θₙ = (1.3 × n) mod 1	Phase (in radians) = θₙ × 2π
0	0.0	0.00
1	0.3	1.884
2	0.6	3.769
3	0.9	5.654
4	0.2	1.257
5	0.5	3.142
6	0.8	5.027
7	0.1	0.628
8	0.4	2.513
9	0.7	4.398
10	0.0	0.00 ← cycle completes

Here's what that looks like graphically:

[GIF] GIF showing how the phase changes every cycle, and plotting the phase values as points on a unit circle [/GIF]

Note that if you put these points in order, they are uniformly distributed between 0 and 2 pi - all of them are the same 0.628 radians apart. This result will hold for any frequency that is not an integer multiple of the target frequency: the phase value will shift in a periodic repetition across time blocks at the target frequency's period, and these phase values will be uniformly distributed from 0 to 2 pi.  

Well it turns out that if you add up sine waves that are uniformly spaced in phase from 0 to 2π, *the sum will always be zero*. [Aside] There's a mathematical proof for this, but it relies on complex exponents that I'm explicitly trying to avoid in my "intuitive" explanation.  I'm sure there's some intuitive argument for this as well, but I'm not smart enough to come up with it. [/Aside] This means that as you add up more and more blocks of 0.25s, *any component frequency signal that is not an integer multiple of the target frequency will disappear*.

sin(a + b) = sin a cos b + sin b cos a
sin(a + nb) = sin a cos nb + sin nb cos a

So what we're left with after adding up a bunch of these blocks is a signal made up exclusively of integer multiple frequencies of the target frequency.  But this might still look complicated; how do you tell which part of the signal, if any, is actually the target frequency itself rather than a multiple?

[Image] the component frequencies of 4 Hz, 8 Hz, 12 Hz, and 16 Hz, with 8 / 12 / 16 phase shifted by a random amount.  Below that, the signal the results when adding these signals together [/Image]

Notice that any signal that is an integer multiple of the target frequency will "spread out" its energy over the width of the window (meaning it will have 2 or more peaks equally spaced throughout the window). In contrast, the target frequency will have exactly 1 peak, and all of its energy concentrated in exactly half the window (with the other half being negative). What we'd like to do is find some way to identify when a portion of the energy is "concentrated" in one part of the period rather than being spread out over the whole period.

Intuitively, we might want to do something like multiply the signal by some transformation function that is "high" for half of the period and "low" for another half of the period, then take the integral (area under the curve) of the result across the whole period.  If the area under the curve is high, that means that there is signficant overlap between the signal being "high" and the "high" half of the transformation function, and if the area under the curve is low, that means most of the time the signal is "high" is during the "low" half of the transformation function [Aside] for simplicity, we assume that the integral of the raw signal itself is zero - i.e. we assume that all component sine waves are cenetered at 0.  This doesn't have to be true - you can have a "DC" component of the signal at 0 Hz that just raises the mean of signal without adding any variation, but the math works out the same.[/Aside]  

Well we already know a function that looks like the transformation function we want: the sine function at the target frequency! If we take the raw signal and multiply it by sin(2pi * t * f), then take the integral from 0 to 2 pi, it will give us precisely this behavior - the resulting value will tell us how "concentrated" the energy is at a given point of the cycle. Of course we have to account for the phase as well - e.g. if the target component frequency of the signal is phase shifted by 180 degrees, then multiplying by the sine wave at 0 phase shift would just yield zero. [Aside] More generally, the value of the integral of a wave multiplied by a phase shifted version of itself over a single cycle will be pi * cos(a - b), where a and b are the respective wave phase shifts. [/Aside] We can solve this by "sliding" the phase of the transformation signal from 0 to 2 * pi and taking the maximum value, which can be achieved conceptually by solving for where the derivative is equal to zero.

In fact, if you take the integral from zero to 2 pi of sin(x) * sin(n * x), it will be 0 for all n >= 2. [Aside] This result holds for any phase shift of either function [/Aside].  For n = 1, the value is instead the amplitude of the wave * pi. [Aside] This result only holds when the two waves are phase aligned. [/Aside] 

So to recap: we have shown that if you have a complex signal made up of a combination of many component frequency sine waves, and you want to investigate whether a target frequency f is one of those component frequencies, you can average a bunch of continguous blocks together with a width of 1 / f.  Any component frequencies that are not integer multiples of f will destructively interfere with themselves, and will average out to 0 with enough blocks, but any component frequencies that are integer multiples of f will still be present.  However, we can take the resulting signal and multiply it by (a possibly phase shifted) sin(2pi * t * f), then integrate over the window width of 1/f seconds.  Doing so will give a positive value proportional to the amplitude of the component frequency if and only if the target frequency is equal to the component frequency, and in all other cases will give zero.

[TODO: validate the above is true through examples.  Specifically, make sure that multiplying a complex wave by sin(x) preserves the characteristics we care about - e.g. that component frequencies multiplied by the target frequency and added together is the same as the complex wave multiplied by the target frequency (not sure what this property is called - associative, distributive, communicative, something else?)]

This is (with a little bit of hand waving) equivalent to the Fourier Transform.  Rather than "breaking up into a bunch of blocks of 1/f," the Fourier Transform is typically conceptualized as "wrapping the function around the origin of the complex plain with a wrapping frequency of f," and rather than "averaging a bunch of blocks together" the Fourier Transform "integrates from -inf to inf."  The Fourier Transform does all of the math using the complex number plane and Euler's Formula (e^(ix) = cos(x) + i * sin(x), with x = pi), and produces a complex number output where the magnitude of the complex number is the amplitude of the frequency component in the signal and the imaginary component of the complex number is the phase of that frequency component.  But conceptually it's doing the exact same thing we did in our attempted intuitive explanation - it's relying on all frequencies that are not integer multiples to cancel themselves out over a long enough time horizon, and its' relying on the symmetry of integer multiple frequencies to cancel out the value of the integral from the other cycles. 

### Discrete Fourier Transforms

At this point you might be asking yourself "why exactly do we care about having a frequency domain representation of audio?"  

One answer is that it is useful for compressing audio.  We talked above about .mp3 using lossy compression - what that is roughly doing is converting the audio to the frequency domain and looking for frequency amplitudes it can drop without impacting perceptual audio quality - e.g. high amplitude ("loud") frequencies tend to mask nearby low amplitude ("quiet") frequencies, so you don't need to bother storing the low amplitude frequency values to reconstruct something that sounds "pretty close" to the orignal signal. 

Another answer is that individual "sounds" are characterized by the frequencies they omit over time, so a frequency domain representation makes audio much easier to analyze and modify. For example, if you can identify the frequencies associated with a particular sound, you could simply set the amplitude of those frequencies to zero in the frequency domain representation and convert back to the time domain, and you'll be left with the original audio with the specific sound "removed".  It is unclear how you would do this operating directly on the time domain signal (or rather, any method of doing this directly in the time domain would have to implicitly be converting to and acting in the frequency domain, so explicitly converting to the frequency domain first greatly simplifies the problem).

So far, we have treated our audio waveform as an infinitely repeating periodic signal; a sum of component frequency sine waves that continue forever in both directions. There are two big problems with this when dealing with real audio:
1) Real audio is "non-stationary" - frequencies come and go, they change amplitude over time, they shift up or down, they reverberate off of nearby surfaces and decay in non-linear ways.  
2) We generally don't have a continuous function describing the waveform over time; instead we have a discrete set of samples that approximate that waveform.

We solve both of these problems using something called the discrete Fourier transform.  Conceptually, the DFT is just a way to apply the Fourier transform to a finite sequence of equally-spaced samples of a function when you don't have access to the function itself.  Here's what the DFT math looks like:

[TODO: insert DFT math] 

DFT works by assuming that the underlying signal is made up of a combination of sine waves, called the component frequencies.  These component frequencies are equally spaced in the frequency domain, and there are exactly as many component frequencies as there are input samples to the DFT.  DFT outputs a sequence of complex-valued coefficients (i.e. with a real component and an imaginary component) where the nth coefficient corresponds to the nth component frequencies.  When the DFT outputs are multiplied by their corresponding sine wave component frequencies, it will produce exactly the same samples that were initially fed into the DFT.

The interval between component frequencies is the reciprocal of the duration of the input sequence - so if your input sequence is 1024 samples with a sample rate of 20 kHz, the DFT interval would be 1 / (1024 / 20,000) ~= 19.5 Hz.  DFT would output coefficients for sine waves at frequencies of 0 Hz, 19.5 Hz, 39 Hz, 58.5 Hz, etc. 

The equal spacing of component frequencies is not a design choice, it is a necessary condition because of how the math works out.  Intuitively, you can think of what's happening here as a system of N equations with N variables (where the sample values are the "target values" and the component frequency coefficients are the variables).  The number of variables has to match the number of equations to find a unique solution, and the variables themselves must have an "orthogonal basis", meaning one variable can't be replicated with a linear combination of two other variables.  If one of your variables is not orthogonal with another, then you don't really have N independent variables, you have N-1 independent variables, and you are not guaranteed to find a unique solution to a systems of equations.  Two waves are orthogonal if the dot product between them is zero.  It turns out the dot product between any two sign waves of different frequencies over a given period is zero... but only if they both complete an intenger number of cycles within that period.  Choosing component frequencies that complete an integer number of cycles within the sample period (aka the duration of the input sequence) guarantees that we have an orthogonal basis.  Here's a good explanation by ChatGPT: https://chatgpt.com/share/684b34af-ac90-800f-8e88-f603d2994fdb

[Aside] All the DFT is doing is taking the dot product of our known basis vectors with the sample values. This is a general method of solving to solving a system of equations with orthonormal basis vectors. [/Aside]

[TODO: confirm specific claims above - e.g. definition of orthogonal basis]

By construction, this means that the highest frequency that DFT outputs a value for is one interval below the sample rate frequency (e.g. 20 kHz - 19.5 Hz = 19,980.5 Hz).  But recall what we said earlier about the Nyquist frequency - the maximum frequency that can be reliably reconstructed is just half the sample rate.  So what do we do with the upper half of the spectrum produced by DFT?

We throw it away of course! It turns out the upper half of the spectrum is guaranteed to be symmetric with (as the complex conjugate of) the lower half, so it contains no additional information not present in the lower half.  Intuitively, you can think of the highest frequency (e.g. 19,980.5 Hz) as being "equivalent" to "the negative of the lowest non-zero frequency" (e.g. -19.5 Hz); If there really was a 19,980.5 Hz signal being measured at a 20,000 Hz sample rate, the signal would complete *almost but not quite* one complete cycle per sample.  This would appear to be slipping very slightly *backwards* along a sine wave at a much lower frequency (specifically, the 20,000 - 19980.5 = 19.5 Hz frequency), and would look identical to a -19.5 Hz sine wave.  [Aside] You may be wondering how it can be true that we have a system of N equations with N independent variables scaling N orthonormal basis vectors and yet we are guaranteed that half of those "independent" variables are always the complex conjugates of the other half (seems like we actually have N/2 independent variables, right?)  I asked ChatGPT and it gave me an answer that I frankly don't have the requisite background to understand: https://chatgpt.com/c/6840d2de-1fd4-800f-af7e-e7571240808a.  The gist of it seems to be that because our input samples are real-valued (i.e. not complex numbers), this constrains the output space of DFT to always be symmetric, and if we used complex input sequence this would no longer be true.  Personally, I'm accepting this as a fuzzy area of my understanding and moving on to more interesting things. [/Aside]

The next obvious question is what happens if the true signal has frequency that is in between the sampling buckets produced by DFT?  The short answer is that the total energy of the true signal will be preserved, but it will be "smeared" through spectral leakage across the integer multiple frequencies produced by the DFT.  Technically some of this energy will be smeared across every frequency band, but in practice the vast majority goes to the nearest frequency bin(s) (intuitively, this happens because the DFT is doing a dot product of the true frequency with the frequency bins, and the nearest bins are "closer to in phase" with the true frequency than farther away bins, which mostly cancel out due to destructive interference.)  

So to recap: for a set of N time-domain samples captured at a sample rate f, we have a method to convert that into a "bucketed" Fourier transform where we get the approximate amplitude of the component frequencies of the original signal at uniformly spaced frequency values.  The number of frequencies we get coefficients for is equal to N.  The frequency interval is equal to f/N.  The "time window" (i.e. the number of milliseconds represented by the DFT spectra output) is equal to N/f.

Notice the tradeoff here - in general we would prefer to capture the spectra over as small of a time window as possible (because frequency energy changes rapidly in the real world, and those dynamics are a core part of what characterizes "sound"), and we would also prefer to capture as many frequencies as possible (because more differentiation in frequencies present gives us more information with which to conduct downstream processing and analysis).  The first constraint would encourage us to use a high sample rate and a low number of samples (maximize N/f), while the second constraint would encourage us to use a high number of samples.  This is referred to as the "time / frequency resolution tradeoff" - the better "time resolution" you get, the worse "frequency resolution" you get, and vice versa.

We already talked about common values of f (16k, 24k, 48k).  Audio processing tasks often use values of N from 128 to 2048, but it depends on the sample rate of the audio and the task at hand.  Typical spectrograms often have window sizes of around 10ms.

### Overlap and Window Functions

You may notice that depending on the dynamics and speed of frequency and amplitude changes, your DFT results might be quite sensitive to window size (or otherwise unstable at time window boundaries).  There are several tricks used in practice to smooth out our time block boundaries, specifically window functions, overlapping frames, and zero padding.

TODO: explain overlapping windows and signal diffusion aka the thread here: https://chatgpt.com/share/686cf5d9-6da0-800f-a8e5-665a16e37f89

### Spectrograms

And now we're finally ready to talk about spectrograms.  A spectrogram is a 2-dimensional graph showing the output of a DFT over time.  The x-axis of the graph is time.  The y-axis of the graph is frequency.  The color of the graph represents the normalized intensity (aka amplitude of the component sine waves, aka magnitude of the complex valued DFT) on a gradient scale of the corresponding frequency bin at the corresponding time:

[Image] Spectrogram examples [/Image]

Strictly speaking, spectrograms have a linear y-axis (since that's what the DFT produces).  However, the more commonly used mel-spectrogram uses a lognormal y-axis (i.e. every "doubling" of frequency is represented by the same size of step up the y-axis).  As discussed earlier, audio mostly behaves in lognormal ways, so displaying the information this way makes it more easily interpretable.  [Aside] in my experience, most people mean "mel-spectrogram" when they say "spectrogram"[/Aside]

Mel-spectrograms are particularly important in an ML context because they allow us to leverage existing image processing techniques for audio analysis.  For example, since convolutions are by construction invariant to spatial translation, it is useful to have perceptually-simillar frequencies laid out in spatially-simillar ways to leverage the inductive bias of CNNS for audio feature extraction.

Note that spectrograms represent frequency amplitudes over time - they don't contain any phase information. The DFT does output phase information, so in principle you could encode that in a spectorgram as well, but in practice it generally isn't done. [Aside] My rough understanding is this is partly because spectrograms of real audio are already encoding SOME of the phase information because of their use of window functions and overlapping frames, partly because jointly modifying amplitude and phase makes downstream modeling tasks harder without adding much benefit, and partly because DFT phase is just an approximation based on assumptions that aren't actually true (such as "there are exactly N component frequencies all equally spaced apart"), so the DFT phase information isn't really the ground truth in the first place. [/Aside]  Instead, conversion of spectrograms back into an audio waveform uses an algorithm to produce phase information that sounds "good enough." The default classical algorithm for this was called Griffin-Lim, [Aside] Griffin-Lim essentially just starts with a random seed and slowly iterates the phase information until it finds a self-consistent phase that can be rendered to an audio wavefrom and then back to a spectrogram indentical to the original. [/Aside] and in the speech domain (particularly text-to-speech models), the model responsible for translating the spectrogram back into an audio waveform (including synthesizing phase information) is known as the "vocoder."  [Aside] The major contribution of original wavenet paper was that it was the first neural vocoder (i.e. a neural network that replaced Griffin-Lim and modeled phase information directly from the spectrogram), which has since become the default approach. [/Aside]  Vocoding today is largely considered a solved problem with no more meaningful headroom in perceptual quality.

## Classical Audio ML
We've now laid the ground work for all the pieces needed to talk about how audio ML models worked before transformers / LLMs came to the forefront circa 2020.  We'll briefly discuss the tasks and models used in this period before moving on to what audio looks like in the new LLM world

### Audio Model Types
There are several ways to slice up the audio ML space.  One important axis for audio data is the *content* of the audio, which generally falls into three categores: speech, music, and open domain (aka "everything else"). Another important axis is whether the task you're trying to accomplish is an analysis task (understanding the content of the audio), a generation task (modifying or creating new audio), or a DSP task (things that are more "signal processing" than they are understanding or generation, such as dereverberation, bandwidth extention, echo cancellation, etc.)

Historically, specialized models were trained for specific tasks within each application area - for example "speech" people and "music" people didn't talk to each other as much as you might think, and speech generation (TTS) and speech analysis (ASR) were almost entirely seperate disciplines with different conferences and academic labs. [Aside] I have always found this somewhat scandalous. It is *beyond obvious* that speech analysis and speech generation ought to *at least* be leveraging shared representations and data even if the core modeling approaches are different.  It was not until audio was adapted into the LLM domain that this became a reality in any meaningful way, and this represents to me an enormous failure of research institutions.[/Aside]  Some signal processing tasks generalize across content typs (e.g. bandwidth extension), but even here it was typical to have seperate models for different content types (e.g. a "speech" bandwidth extention model that is different from the "music" bandwidth extension model)

Of course these categories are artificially discrete, and there are plenty of areas that span these boundaries.
Speech-to-speech, speech-to-translated-text, universal separation, removal

Orthogonal to these use cases 

Speech ASR
TTS
Dynamic EQ
Source Separation / Speech enhancement / speech & music removal (dubbing, DMCA takedown requests) 
De-essing
Reverber / dereverb

### Directional Beamforming
Directional beamforming is a processing technique that allows an audio signal recorded on two or more mics to be decomposed based on the direction the sound came from.  Essentially this relies on the fact that the delay between when mic 1 and mic 2 hear the same sound is a function of the angle of the sound source relative to the microphones and the distance of the mics from each other.  For only two microphones a known distance apart, a given audio delay is enoug to specify a parabolic cone [TODO: name for this?] along which the sound must have originated; by adding a third mic you can in theory specify a specific point (including distance) of the orignal audio source (so long as that point is not co-planar with the 3 mics).

In practice what this means is that you can take audio recorded on a microphone array with known dimensions and filter it (i.e. delay one and add them together) so that sounds not coming from one particular direction cancel each other out, leaving you only the sounds coming from a particular direction.  This is useful when you want to do things like record audio coming from right in front of a camera while supressing any audio coming from the ambient environment. 


Dynamic beamforming - "delay and sum" - essentially you figure out the expected delay for sound coming from a particular direction, then you add the spectrograms from each mic at that delay.  This will create "constructive intererence" for signals coming from that direction, and "destrictive" interference for signals coming from other directions (seems like this wouldn't work in the presence of constant sounds?)

Audio engineering / mastering

### ASR Circa 2020
wav2vec
BEST-RQ
### TTS Circa 2020
Frontend, XXX, vocoder
Tacotron
Griffin-Lim
wavenet
Convolutional Neural Networks

## LLMs
Transformers (cross-attention, scale, benefits vs. LSTM / RNNs, scale scale scale)
ChatGPT - Generative Pretrained Transformer
Autoregressive token prediction
Encoder-only vs. Encoder-decoder models
Sampling methodology (temperature, top-k sampling, greedy sampling)
Tokenizers and how they impact performance (capital vs. lowercase letters, sequences of numbers / math, number of r's in strawberry)
Discrete vs. continuous output (cross entropy loss, modeling fundamentally tokenized data (sort of, given first thing transformer does is project tokens into continuous space))
Note: no time component! fundamentally different from audiovisual data

## Audio LLMs

## Audio Tokenizers
Wav2Vec
w2v-bert
Spectrograms
Soundstream (RVQ)

AudioLM
Tortise-TTS (ElevenLabs)

## Audio-enabled multimodel LLMs
AudioPaLM
ChatGPT
Gemini
Sesame Labs (/ Maya? Apparently Johan contributed to that too)
Streaming / full duplex
Moshi model- https://github.com/kyutai-labs/moshi
Facebook superintelligence lab?
Lab that Miana went to after Google

## Major open questions for Audio LLMs
Tokenizers
Model architecture (side channeling information like speaker identity)
Cross-modal generalization vs. specialization
Diffusion vs. autoregressive token prediction
Fine tuning vs. LoRA vs. shoving history in context prompt window
Zero and few shot tuning / data efficiency / new algorithms needed
